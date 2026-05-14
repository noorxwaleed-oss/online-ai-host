import bs4
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader

def load_data(source):
    if source.startswith("http"):
        loader = WebBaseLoader(
            web_path=(source,),
            bs_kwargs=dict(parse_only=bs4.SoupStrainer(name=("article", "h1", "h2", "h3", "p")))
        )
    else:
        loader = PyPDFLoader(source)
    return loader.load()