from flask import Flask,render_template,request
import pickle
import numpy as np

popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    # Get list of available books for dropdown
    available_books = list(pt.index)
    return render_template('recommend.html', available_books=available_books)

@app.route('/recommend_books',methods=['post'])
def recommend():
    user_input = request.form.get('user_input')
    
    # Check if user input is empty
    if not user_input:
        available_books = list(pt.index)
        return render_template('recommend.html', data=None, error="Please select a book from the dropdown.", available_books=available_books)
    
    # Check if user input exists in pivot table
    if user_input not in pt.index:
        available_books = list(pt.index)
        return render_template('recommend.html', data=None, error="Book not found. Please select a valid book from the dropdown.", available_books=available_books)
    
    try:
        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            if not temp_df.empty:
                item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
                item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
                item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
                data.append(item)

        print(data)
        available_books = list(pt.index)
        return render_template('recommend.html', data=data, error=None, available_books=available_books)
        
    except Exception as e:
        print(f"Error in recommend function: {str(e)}")
        available_books = list(pt.index)
        return render_template('recommend.html', data=None, error="An error occurred while processing your request.", available_books=available_books)

if __name__ == '__main__':
    app.run(debug=True)