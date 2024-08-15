import os
from flask import Flask, render_template, request
from dash_application import create_dash_app
import pickle
import pandas as pd

# Load the PCA and scaler objects from the pickle file
with open('/home/user/pcaso/model/pca_scaler.pkl', 'rb') as file:
    pca_scaler = pickle.load(file)
    pca = pca_scaler['pca']
    scaler = pca_scaler['scaler']
    le = pca_scaler['le']

with open('/home/user/pcaso/model/final-model.pkl', 'rb') as file:
    model = pickle.load(file)

data = pd.read_csv('/home/user/pcaso/data/DR18.csv')

app = Flask(__name__)

create_dash_app(app)

def classify_new_data(new_data):
    df_new = new_data.copy()
    # Apply PCA transformation using the already fitted PCA
    pca_features = pca.transform(df_new[['u', 'g', 'r', 'i', 'z']])
    df_new = pd.concat((df_new, pd.DataFrame(pca_features, columns=['PCA_1', 'PCA_2', 'PCA_3'])), axis=1)
    df_new.drop(['u', 'g', 'r', 'i', 'z'], axis=1, inplace=True)
    # Scale features
    scaled_features = scaler.transform(df_new.drop('class', axis=1, errors='ignore'))
    # Make predictions
    predictions = model.predict(scaled_features)
    df_new['Predicted_class'] = le.inverse_transform(predictions)
    return df_new

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/background")
def background():
    return render_template('background.html')

@app.route("/edaizer/")
def dashboard():
    return render_template('edaizer.html')

@app.route('/classifier/', methods=['GET', 'POST'])
def classifier():
    if request.method == 'POST':
        try:
            # Get form data
            form_data = {
                'ra': float(request.form['field1']),
                'dec': float(request.form['field2']),
                'u': float(request.form['field3']),
                'g': float(request.form['field4']),
                'r': float(request.form['field5']),
                'i': float(request.form['field6']),
                'z': float(request.form['field7']),
                'redshift': float(request.form['field8']),
                'plate': int(request.form['field9']),
                'mjd': int(request.form['field10']),
                'fiberid': int(request.form['field11']),
            }
            
            # Convert form data to DataFrame
            df_new = pd.DataFrame([form_data])
            
            # Classify new data
            result = classify_new_data(df_new)
            classification_result = result['Predicted_class'].iloc[0]

            filtered_data = data.loc[data['class'] == classification_result, ['ra', 'dec']]
            selected_row = filtered_data.sample(n=1)  # Select a random row

            # Use the selected row's ra and dec to fetch the image from SDSS API
            ra_selected = selected_row['ra'].values[0]
            print(ra_selected)
            dec_selected = selected_row['dec'].values[0]
            print(dec_selected)

            sdss_api_url = f"http://skyserver.sdss.org/dr16/SkyServerWS/ImgCutout/getjpeg?ra={ra_selected}&dec={dec_selected}&scale=0.4&height=512&width=512&opt=GO"
            image_url = sdss_api_url
            
            # Render the HTML template with the classification result
            return render_template('classifier.html', classification_result=classification_result, image_url=image_url)
    
        except Exception as e:
            return render_template('classifier.html', error=str(e))
    
    return render_template('classifier.html')

@app.route("/research")
def research():
    return render_template('research.html')

@app.route("/documentation")
def documentation():
    return render_template('documentation.html')

def main():
    app.run(port=int(os.environ.get('PORT', 80)))

if __name__ == "__main__":
    main()
