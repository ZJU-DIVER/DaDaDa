from transformers import XLMRobertaTokenizer
import torch
import pandas as pd
from transformers import XLMRobertaModel
def process_in_chunks(filepath, model_dir, model_name, tokenizer_dir,layer, chunk_size):
    tokenizer = XLMRobertaTokenizer.from_pretrained(tokenizer_dir)
    embedding_model = XLMRobertaModel.from_pretrained(model_dir)

    is_first_chunk = True

    # read the data in chunks
    for chunk in pd.read_csv(filepath, chunksize=chunk_size):
        print(chunk.shape)
        chunk['text'] = 'title:' + chunk['title'] + ' description:' + chunk['description']
        text_list = chunk['text'].tolist()

        # get the embeddings in chunks
        embeddings = []
        for i in range(0, len(text_list), chunk_size):
            batch_texts = text_list[i:i + chunk_size]
            batch_embeddings = get_word_embeddings(batch_texts, tokenizer, embedding_model, layer)
            embeddings.append(batch_embeddings)

        embeddings = torch.cat(embeddings, dim=0)
        embeddings_df = pd.DataFrame(embeddings.cpu().numpy())
        # add the platform column
        embeddings_df['platform'] = chunk['platform'].tolist()
        embeddings_df['title'] = chunk['title'].tolist()

        # store the embeddings in a CSV file
        if is_first_chunk:
            embeddings_df.to_csv(f'{model_name}_{layer}_embeddings.csv', index=False)
            is_first_chunk = False
        else:
            embeddings_df.to_csv(f'{model_name}_{layer}_embeddings.csv', mode='a', index=False, header=False)

def get_word_embeddings(texts, tokenizer, model, layer):
    inputs = tokenizer(texts, return_tensors='pt', padding=True, truncation=True, max_length=512)
    if torch.cuda.is_available():
        model.cuda()
        inputs = {k: v.cuda() for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)
    # get the hidden states
    hidden_states = outputs.hidden_states[layer]
    # get the CLS token embeddings
    cls_embeddings = hidden_states[:, 0, :]
    return cls_embeddings


if __name__ == '__main__':
    seed = 42

    model_name = 'xlm-r-large'
    tokenizer_dir = 'FacebookAI/xlm-roberta-large'
    model_dir = '../../classification/best_model/xlm-r-large'


    # middle layer
    process_in_chunks("final_data.csv", model_dir, model_name, tokenizer_dir, layer = 12, chunk_size=500)
    # last layer
    process_in_chunks("final_data.csv", model_dir, model_name, tokenizer_dir, layer = 24, chunk_size=500)