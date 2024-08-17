
const {createProxyMiddleware} = require('http-proxy-middleware')

module.exports = function (app){
    
    app.use(
        ['/api'],
        createProxyMiddleware({
            target:'http://localhost:9200',
            changeOrigin:true,
        })
    )
}

/*:{
                gameApiPattern:"",
                otherApiPattern:""
                // '^/api/test/':'/test/',
                // '^/api/new_project':'/new_project/',
                //'^/api/project_list':'/project_list/',
                //'^/api/project_info':'/project_list/',
                //'^/api':"" //old rules, deprecated
            } */