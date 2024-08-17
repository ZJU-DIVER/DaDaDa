import argparse
from transformers import BertTokenizer, XLMRobertaTokenizer
from datasets import Dataset
import pandas as pd
import numpy as np
import os
import shutil
import torch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from transformers import BertForSequenceClassification, Trainer, TrainingArguments, XLMRobertaForSequenceClassification
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.metrics import classification_report, confusion_matrix
from torch.utils.data import DataLoader
def prepare_data(filepath, seed):
    # read data
    df = pd.read_csv(filepath)

    # remove null values
    df = df.dropna(subset=['title', 'description', 'category']).reset_index(drop=True)

    # merge title and description
    df['text'] = 'title:' + df['title'] + ' description:' + df['description']
    df = df[['text', 'category']]
    # split data into training and testing sets
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=seed)

    # convert string labels to numerical labels
    label_encoder = LabelEncoder()
    train_df['category'] = label_encoder.fit_transform(train_df['category'])
    test_df['category'] = label_encoder.transform(test_df['category'])

    return train_df, test_df, label_encoder

def prepare_and_tokenize_data(df, model_dir, model_name):
    if model_name == 'mbert':
        tokenizer = BertTokenizer.from_pretrained(model_dir)
    else:
        tokenizer = XLMRobertaTokenizer.from_pretrained(model_dir)

    # Tokenizing the text
    def tokenize_function(examples):
        return tokenizer(examples['text'], padding=True, truncation=True, max_length=512)

    dataset = Dataset.from_pandas(df)
    tokenized_dataset = dataset.map(tokenize_function, batched=True)

    return tokenized_dataset


def fine_tune_model(train_dataset, val_dataset, model_dir, model_name, seed):
    if model_name == 'mbert':
        model = BertForSequenceClassification.from_pretrained(model_dir,
                                                          num_labels=12)
    else:
        model = XLMRobertaForSequenceClassification.from_pretrained(model_dir,
                                                          num_labels=12)

    if model_name == 'xlm-r-large':
        batch_size = 32
    else:
        batch_size = 64

    if torch.cuda.is_available():
        model.cuda()

    # Define the training arguments
    training_args = TrainingArguments(
        output_dir='./results/' + model_name,  # The output directory
        num_train_epochs=20,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        warmup_steps=500,  # number of warmup steps for learning rate scheduler
        weight_decay=0.01,
        logging_dir='./logs',  # directory for storing logs
        logging_steps=10,
        load_best_model_at_end=True,
        evaluation_strategy="epoch",  # evaluate at the end of each epoch
        save_strategy="epoch",
        metric_for_best_model = "f1",
        seed = seed
    )

    # training with trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )

    trainer.train()
    return trainer


def compute_metrics(p):
    preds = np.argmax(p.predictions, axis=1)
    labels = p.label_ids
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted')
    acc = accuracy_score(labels, preds)

    return {"accuracy": acc, "f1": f1, "precision": precision, "recall": recall}

def evaluate_model(trainer, test_dataset):
    predictions = trainer.predict(test_dataset)
    preds = np.argmax(predictions.predictions, axis=1)
    print(classification_report(test_dataset['labels'], preds, target_names=label_encoder.classes_, digits=3))
    print(confusion_matrix(test_dataset['labels'], preds))
    # compute the accuracy
    acc = accuracy_score(test_dataset['labels'], preds)
    print(f"Accuracy: {acc:.4f}")

def create_data_loader(tokenized_dataset):
    def collate_fn(batch):
        # Convert each feature in the batch to tensor
        keys = batch[0].keys()
        batch_tensors = {}
        for key in keys:
            batch_tensors[key] = torch.tensor([x[key] for x in batch])
        return batch_tensors

    loader = DataLoader(tokenized_dataset, batch_size=16, shuffle=True, collate_fn=collate_fn)
    return loader

def load_and_evaluate_model(model_dir, model_name, test_dataset, label_encoder):
    # load the best model
    if model_name == 'mbert':
        model = BertForSequenceClassification.from_pretrained(model_dir)
    else:
        model = XLMRobertaForSequenceClassification.from_pretrained(model_dir)

    if torch.cuda.is_available():
        model.cuda()

    model.eval()

    # create DataLoader
    test_loader = create_data_loader(test_dataset)

    # initialize evaluation metrics
    all_preds = []
    all_labels = []

    # iterate over the test set
    model.eval()
    with torch.no_grad():
        for batch in test_loader:
            inputs = {key: batch[key].cuda() for key in batch if key != 'labels'}
            labels = batch['labels'].cuda()
            outputs = model(**inputs)
            preds = torch.argmax(outputs.logits, axis=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    # print the classification report and confusion matrix
    print(classification_report(all_labels, all_preds, target_names=label_encoder.classes_, digits=3))
    print(confusion_matrix(all_labels, all_preds))
    # compute the accuracy
    acc = accuracy_score(all_labels, all_preds)
    print(f"Accuracy: {acc:.4f}")

def get_model_config(model_choice):
    if model_choice == 'mbert':
        return 'google-bert/bert-base-multilingual-cased', 'mbert'
    elif model_choice == 'xlm-r-large':
        return 'FacebookAI/xlm-roberta-large', 'xlm-r-large'
    elif model_choice == 'xlm-r-base':
        return 'FacebookAI/xlm-roberta-base', 'xlm-r-base'
    else:
        raise ValueError(f"Unknown model choice: {model_choice}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Choose a model for the task.")
    parser.add_argument('--model', type=str, required=True, choices=['mbert', 'xlm-r-large', 'xlm-r-base'],
                        help="Model choice: 'mbert', 'xlm-r-large', or 'xlm-r-base'")
    parser.add_argument('--mode', type=str, required=True, default='test', choices=['train', 'test'],
                        help = "Mode choice: 'train' or 'test'")
    args = parser.parse_args()
    model_dir, model_name = get_model_config(args.model)
    mode = args.mode

    seed = 42

    train_df, test_df, label_encoder = prepare_data('../../data/final_data.csv', seed)
    train_df, val_df = train_test_split(train_df, test_size=0.25, random_state=seed)

    train_dataset = prepare_and_tokenize_data(train_df, model_dir, model_name)
    val_dataset = prepare_and_tokenize_data(val_df, model_dir, model_name)
    test_dataset = prepare_and_tokenize_data(test_df, model_dir, model_name)

    # rename the 'category' field
    train_dataset = train_dataset.rename_column("category", "labels")
    val_dataset = val_dataset.rename_column("category", "labels")
    test_dataset = test_dataset.rename_column("category", "labels")

    # remove the text and __index_level_0__ columns
    train_dataset = train_dataset.remove_columns(["text", "__index_level_0__"])
    val_dataset = val_dataset.remove_columns(["text", "__index_level_0__"])
    test_dataset = test_dataset.remove_columns(["text", "__index_level_0__"])

    if mode == 'train':
        # fine-tune the model
        trainer = fine_tune_model(train_dataset, val_dataset, model_dir, model_name, seed)

        # rename the best model checkpoint directory
        best_model_dir = trainer.state.best_model_checkpoint
        new_model_dir = "./best_model/" + model_name

        # Copying the best model checkpoint to the new directory
        if best_model_dir is not None:
            if os.path.exists(new_model_dir):
                shutil.rmtree(new_model_dir)
            shutil.copytree(best_model_dir, new_model_dir)

        print(f"Best model saved to: {new_model_dir}")

        # Evaluate the model on the test dataset
        evaluate_model(trainer, test_dataset)

    elif mode == 'test':
        best_model_dir = "./best_model/" + model_name
        # Evaluate the model on the test dataset
        load_and_evaluate_model(best_model_dir, model_name, test_dataset, label_encoder)



