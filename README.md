# wiki-js-maintenance-tools
维护WIKI.js项目使用的常用代码工具

# 使用
1. 待上传的文件被放置在/data下
   - 其中外来的卡牌数据被放置在/data/{locale}/card_json
   - 外来的卡牌数据，需要通过执行脚本/src/wiki_synchronizer.py将数据同步到/data/card文件夹下
   - 非外来数据(规则等)，直接在本地进行维护即可
2. 执行脚本/src/wiki_uploader.py上传数据
   - 默认上传到测试环境(如本地有)
   - 环境配置在.env文件夹中