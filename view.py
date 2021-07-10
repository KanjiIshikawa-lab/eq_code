import eel
import desktop
import search

app_name = "html"
end_point = "index.html"
size = (600,200)

@ eel.expose

def shop_search(search_keyword):
    search.shop_search(search_keyword)

desktop.start(app_name,end_point,size)

