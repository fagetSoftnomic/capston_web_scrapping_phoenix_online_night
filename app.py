from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
web_Address = "https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31"
web_content = requests.get(web_Address).text
web_content_soup = BeautifulSoup(web_content, "html.parser")
div_contents = web_content_soup.find('div', attrs={'class': 'lister-list'})

movie_list = []

for div_lister_item_content in div_contents.find_all('div', attrs={'class': 'lister-item-content'}):
    
    title_header = div_lister_item_content.find('h3')
    title_tag = title_header.find('a')
    title = title_tag.text
    
    #Find Rating Bar
    div_rating_bar = div_lister_item_content.find('div', attrs={'class': 'ratings-bar'})
    if div_rating_bar is None:
        rating = 0
    elif div_rating_bar is not None:
        rating_tag = div_rating_bar.find('div', attrs={'class': 'inline-block ratings-imdb-rating'})
        rating = rating_tag.text.strip()
        
        #Find Metascore --> Metasocre inside the rating bar DIV
        div_metascore = div_rating_bar.find('div', attrs={'class': 'inline-block ratings-metascore'})
        if div_metascore is None:
            metascore = 0
        elif div_metascore is not None:
            metascore = div_metascore.find('span').text.strip()
       
    #Find Vote
    vote_paragraph = div_lister_item_content.find('p', attrs={'sort-num_votes-visible'})
    if vote_paragraph is None:
        vote = 0
    else:
        vote_paragraph_span = vote_paragraph.find_all('span')[1].text.replace(",", "")
        vote = vote_paragraph_span

    
    movie_list.append((title, rating))#, metascore, vote))

movie_list = movie_list[::-1]

#change into dataframe
data = pd.DataFrame(movie_list, columns = ('movie_title','movie_rating'))#,'_____'))
#insert data wrangling here
data['movie_title'] = data['movie_title'].astype('category')
data['movie_rating'] = data['movie_rating'].astype('float64')

df_top_seven_movies = data.sort_values(by='movie_rating', ascending=False).head(7)

df_top_seven_movies = df_top_seven_movies.set_index('movie_title')
#data

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df_top_seven_movies["movie_rating"].mean().round(2)}' #be careful with the " and ' 
	# card_data = f'{data["fx_rate"].round(2)}' #be careful with the " and '

	# generate plot
	ax = df_top_seven_movies.plot(figsize = (20,9)) 
	print(ax)
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)