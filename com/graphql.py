# ----------------------------------------
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @author       : 
# @email        : 
# @time         : 2025/8/22 15:04
# @file         : graphql.py
# @Desc         :
# -----------------------------------------

# import from official
import json
from typing import Dict, Optional, List, Any
# import from third-party
import requests
# import from self-defined


class WikiJSGraphQLClient:
    """
    Wiki.js GraphQL客户端，用于与Wiki.js服务器进行交互

    支持认证、查询页面、创建页面、更新页面、删除页面等操作
    """

    def __init__(self, base_url: str, api_token: Optional[str] = None):
        """
        初始化Wiki.js客户端

        :param base_url: Wiki.js服务器基础URL，例如: https://wiki.example.com
        :param api_token: API访问令牌，可选。如果未提供，需要先调用login方法进行认证
        """
        self.base_url = base_url.rstrip('/')
        self.graphql_endpoint = f"{self.base_url}/graphql"
        self.api_token = api_token
        self.headers = {
            "Content-Type": "application/json",
        }

        # 如果提供了API令牌，添加到请求头
        if self.api_token:
            self.headers["Authorization"] = f"Bearer {self.api_token}"

    def login(self, email: str, password: str) -> bool:
        """
        使用用户名密码登录Wiki.js，获取并存储API令牌

        :param email: 登录邮箱
        :param password: 登录密码
        :return: 登录成功返回True，否则返回False
        """
        query = """
        mutation login($email: String!, $password: String!) {
            auth {
                login(email: $email, password: $password) {
                    jwt
                    user {
                        id
                        email
                        name
                    }
                }
            }
        }
        """

        variables = {
            "email": email,
            "password": password
        }

        response = self.graphql_request(query, variables, include_auth=False)

        if response and "data" in response and "auth" in response["data"] and "login" in response["data"]["auth"]:
            self.api_token = response["data"]["auth"]["login"]["jwt"]
            self.headers["Authorization"] = f"Bearer {self.api_token}"
            return True

        return False

    def graphql_request(self, query: str, variables: Optional[Dict] = None, include_auth: bool = True) -> Optional[
        Dict]:
        """
        发送GraphQL请求到Wiki.js服务器

        :param query: GraphQL查询或变更字符串
        :param variables: 查询变量字典
        :param include_auth: 是否包含认证头，默认为True
        :return: 服务器响应的JSON数据，出错时返回None
        """
        if not variables:
            variables = {}

        payload = {
            "query": query,
            "variables": variables
        }

        # 复制基础头信息
        headers = self.headers.copy()

        # 如果不需要认证，移除认证头
        if not include_auth and "Authorization" in headers:
            del headers["Authorization"]

        try:
            response = requests.post(
                self.graphql_endpoint,
                headers=headers,
                data=json.dumps(payload)
            )

            response.raise_for_status()
            result = response.json()

            # 检查是否有GraphQL错误
            if "errors" in result:
                print(f"GraphQL错误: {result['errors']}")
                return None

            return result

        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return None

    def get_page(self, page_id: int) -> Optional[Dict]:
        """
        获取指定ID的页面详情

        :param page_id: 页面ID
        :return: 页面信息字典，出错时返回None
        """
        query = """
        query getPage($id: Int!)
        {
          pages {
            single (id: $id) {
              path
              title
              createdAt
              updatedAt
            }
          }
        }
        """

        variables = {
            "id": page_id
        }

        response = self.graphql_request(query, variables)

        if response and "data" in response and "pages" in response["data"]:
            return response["data"]["pages"]["single"]

        return None

    def get_page_by_path(self, path: str, locale: str) -> Optional[Dict]:
        """
        通过路径获取页面详情

        :param path: 页面路径，例如: "docs/api"
        :param locale: 语言代码，例如: "en"
        :return: 页面信息字典，出错时返回None
        """
        query = """
        query getPageByPath($path: String!, $locale: String!) {
            pages {
                singleByPath(path: $path, locale: $locale) {
                    id
                    path
                    hash
                    title
                    description
                    isPrivate
                    isPublished
                    privateNS
                    publishStartDate
                    publishEndDate
                    tags {
                      id
                      tag
                      title
                      createdAt
                      updatedAt
                    }
                    content
                    render
                    toc
                    contentType
                    createdAt
                    updatedAt
                    editor
                    locale
                    scriptCss
                    scriptJs
                    authorId
                    authorName
                    authorEmail
                    creatorId
                    creatorName
                    creatorEmail
                }
            }
        }
        """

        variables = {
            "path": path,
            "locale": locale
        }

        response = self.graphql_request(query, variables)

        if response and "data" in response and "pages" in response["data"]:
            return response["data"]["pages"]["singleByPath"]

        return None

    def list_pages(self, limit: int = 50) -> Optional[List[Dict]]:
        """
        获取页面列表

        :param limit: 最大返回数量
        :return: 页面列表，出错时返回None
        """
        query = """
        query listPages($limit: Int)
        {
          pages {
            list (limit: $limit, orderBy: TITLE) {
              id
              path
              locale
              title
              description
              contentType
              isPublished
              isPrivate
              privateNS
              createdAt
              updatedAt
              tags
            }
          }
        }
        """

        variables = {
            "limit": limit,
        }

        response = self.graphql_request(query, variables)

        if response and "data" in response and "pages" in response["data"]:
            return response["data"]["pages"]["list"]

        return None

    def create_page(self, title: str, locale: str, path: str, content: str, description: str = "", is_published: bool = True, is_private: bool = False,
                    editor: str = "markdown", tags: List[str] = None) -> Optional[Dict]:
        """
        创建新页面

        :param title: 页面标题
        :param locale: 语言代码
        :param path: 页面路径
        :param content: 页面内容
        :param description: 页面描述
        :param is_published: 是否发布
        :param editor: 编辑器类型，默认为"markdown"
        :param tags: 标签列表
        :return: 创建的页面信息，出错时返回None
        """
        if tags is None:
            tags = []

        query = """
        mutation createPage(
            $content: String!, 
            $description: String!,
            $editor: String!, 
            $isPublished: Boolean!,
            $isPrivate: Boolean!,
            $locale: String!,
            $path: String!,
            $tags: [String]!,
            $title: String!
        ) {
            pages {
                create(
                    content: $content,
                    description: $description,
                    editor: $editor,
                    isPublished: $isPublished,
                    isPrivate: $isPrivate,
                    locale: $locale,
                    path: $path,
                    tags: $tags,
                    title: $title
                ) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                    page {
                        id
                    }
                }
            }
        }
        """
        variables = {
            "content": content,
            "description": description,
            "editor": editor,
            "isPublished": is_published,
            "isPrivate": is_private,
            "locale": locale,
            "path": path,
            "tags": tags,
            "title": title
        }

        response = self.graphql_request(query, variables)

        if response and "data" in response and "pages" in response["data"]:
            return response["data"]["pages"]["create"]

        return None

    def update_page(
            self,
            page_id: int,
            content: Optional[str] = None,
            description: Optional[str] = None,
            editor: Optional[str] = None,
            isPrivate: Optional[bool] = False,
            isPublished: Optional[bool] = True,
            locale: Optional[str] = None,
            path: Optional[str] = None,
            tags: Optional[List[str]] = None,
            title: Optional[str] = None,
    ) -> Optional[Dict]:  # 新增参数
        """
        更新现有页面
        :param page_id: 页面ID
        :param content: 页面内容
        :param description: 页面描述
        :param editor: 编辑器类型
        :param isPrivate: 是否私有
        :param isPublished: 是否发布
        :param locale: 语言代码
        :param path: 页面路径
        :param tags: 标签列表
        :param title: 页面标题
        :return: 更新后的页面信息
        """

        query = """
        mutation updatePage(
            $id: Int!,
            $content: String,
            $description: String,
            $editor: String,
            $isPrivate: Boolean,
            $isPublished: Boolean,
            $locale: String,
            $path: String,
            $tags: [String],
            $title: String
        ) {
            pages {
                update(
                    id: $id, 
                    content: $content,
                    description: $description,
                    editor: $editor,
                    isPrivate: $isPrivate,
                    isPublished: $isPublished,
                    locale: $locale,
                    path: $path,
                    tags: $tags,
                    title: $title
                ) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                    page {
                        id
                    }
                }
            }
        }
        """

        variables: Dict[str, Any] = {
            "id": page_id,
            "isPrivate": isPrivate,
            "isPublished": isPublished
        }

        # 动态添加非None的可选参数
        if title is not None:
            variables["title"] = title
        if path is not None:
            variables["path"] = path
        if content is not None:
            variables["content"] = content
        if editor is not None:
            variables["editor"] = editor
        if tags is not None:
            variables["tags"] = tags
        if locale is not None:
            variables["locale"] = locale
        if description is not None:
            variables["description"] = description

        # 发送请求
        response = self.graphql_request(query, variables)

        # 处理响应
        if response and "data" in response and "pages" in response["data"]:
            return response["data"]["pages"]["update"]

        return None

    def delete_page(self, page_id: int) -> bool:
        """
        删除指定页面

        :param page_id: 要删除的页面ID
        :return: 删除成功返回True，否则返回False
        """
        query = """
        mutation deletePage($id: Int!) {
            pages {
                delete(id: $id)
            }
        }
        """

        variables = {
            "id": page_id
        }

        response = self.graphql_request(query, variables)

        if response and "data" in response and "pages" in response["data"]:
            return response["data"]["pages"]["delete"]

        return False

    def get_tags(self) -> Optional[List[Dict]]:
        """
        获取所有标签

        :return: 标签列表，出错时返回None
        """
        query = """
        query getTags {
            tags {
                list {
                    id
                    name
                    color
                    pageCount
                }
            }
        }
        """

        response = self.graphql_request(query)

        if response and "data" in response and "tags" in response["data"]:
            return response["data"]["tags"]["list"]

        return None


# 使用示例
if __name__ == "__main__":
    import os
    from util import pathUtil
    from dotenv import load_dotenv

    load_dotenv(pathUtil.getEnvFile())

    # 初始化客户端
    wiki_url = os.getenv("WIKI_URL")
    wiki_api_token = os.getenv("WIKI_API_TOKEN")
    wiki_client = WikiJSGraphQLClient(wiki_url, wiki_api_token)

    # 登录（如果没有API令牌）
    # login_success = wiki_client.login("your-email@example.com", "your-password")
    # if not login_success:
    #     print("登录失败")
    #     exit(1)

    # 或者直接使用API令牌
    # wiki_client = WikiJSGraphQLClient("https://your-wiki-instance.com", "your-api-token")

    # 获取页面列表
    # pages = wiki_client.list_pages(limit=10)
    # if pages:
    #     print(f"找到 {len(pages)} 个页面:")
    #     for page in pages:
    #         print(f"{page['id']} - {page['title']} ({page['path']})")
    #         pageId = page['id']

    # 根据路径搜索页面
    # page_info = wiki_client.get_page_by_path("home", "zh")
    # print(page_info)

    # 创建新页面示例
    # new_page = wiki_client.create_page(
    #     title="新API测试页面",
    #     description="这是一个通过API创建的新页面",
    #     locale="zh",
    #     path="api-test-page-3",
    #     content="# 这是一个测试页面\n\n通过API创建的示例页面",
    #     tags=["api", "test"]
    # )
    # if new_page:
    #     create_result = new_page["responseResult"]
    #     page_info = new_page["page"]
    #     if create_result.get("succeeded", False):
    #         print(f"创建成功: {page_info.get('id', -1)}")
    #     else:
    #         print(f"创建失败: {create_result.get('message')}")

    # 获取页面详情示例
    page_info = wiki_client.get_page(page_id=6)
    print(page_info)
    resp = wiki_client.update_page(
        page_id=3,
        title="更新后的API测试页面",
        description="这是一个通过API更新的页面",
        locale="zh",
        content="# 这是一个测试页面\n\n通过API更新的示例页面",
        tags=["api", "test", "updated"],
    )

    if resp:
        resp_result = resp["responseResult"]
        page_info = resp["page"]
        if resp_result.get("succeeded", False):
            print(f"创建成功: {page_info.get('id', -1)}")
        else:
            print(f"创建失败: {resp_result.get('message')}")