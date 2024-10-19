from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import io

app = Flask(__name__)


def find_optimal_clusters(scaled_features, max_clusters=10):
    best_score = -1
    best_n_clusters = 2
    silhouette_scores = {}

  
    for n_clusters in range(2, max_clusters + 1):
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(scaled_features)
        score = silhouette_score(scaled_features, cluster_labels)
        silhouette_scores[n_clusters] = score

        if score > best_score:
            best_score = score
            best_n_clusters = n_clusters

    return best_n_clusters, silhouette_scores

@app.route('/cluster', methods=['POST'])
def cluster():
 
    file = request.files['file']
    df = pd.read_csv(file)

    client_usage = df.groupby('client_id').agg(
        avg_bw_requested=('bw_requested', 'mean'),
        peak_bw_requested=('bw_requested', 'max'),
        variance_bw=('bw_requested', 'var')
    ).reset_index()

 
    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
    peak_times = df.groupby('client_id').apply(
        lambda x: x.loc[x['bw_requested'].idxmax()]['hour']).reset_index(name='peak_usage_hour')

 
    features = pd.merge(client_usage, peak_times, on='client_id')

    
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features[['avg_bw_requested', 'peak_bw_requested', 'variance_bw', 'peak_usage_hour']])

   
    best_n_clusters, silhouette_scores = find_optimal_clusters(scaled_features)

    
    kmeans = KMeans(n_clusters=best_n_clusters, random_state=42)
    features['cluster'] = kmeans.fit_predict(scaled_features)

    cluster_summary = features.groupby('cluster').agg(
        avg_bw=('avg_bw_requested', 'mean'),
        max_bw=('peak_bw_requested', 'mean'),
        variance=('variance_bw', 'mean'),
        clients_in_cluster=('client_id', 'count')
    ).reset_index()


    cluster_summary_json = cluster_summary.to_dict(orient='records')
    silhouette_scores_json = {str(k): v for k, v in silhouette_scores.items()} 

    return jsonify({
        'best_n_clusters': best_n_clusters,
        
        'cluster_summary': cluster_summary_json
    })

@app.route('/clients_in_cluster', methods=['POST'])
def clients_in_cluster():

    file = request.files['file']
    cluster_number = int(request.form['cluster_number'])  

    df = pd.read_csv(file)

   
    client_usage = df.groupby('client_id').agg(
        avg_bw_requested=('bw_requested', 'mean'),
        peak_bw_requested=('bw_requested', 'max'),
        variance_bw=('bw_requested', 'var')
    ).reset_index()

    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
    peak_times = df.groupby('client_id').apply(
        lambda x: x.loc[x['bw_requested'].idxmax()]['hour']).reset_index(name='peak_usage_hour')


    features = pd.merge(client_usage, peak_times, on='client_id')

   
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features[['avg_bw_requested', 'peak_bw_requested', 'variance_bw', 'peak_usage_hour']])


    best_n_clusters, _ = find_optimal_clusters(scaled_features)  
    kmeans = KMeans(n_clusters=best_n_clusters, random_state=42)
    features['cluster'] = kmeans.fit_predict(scaled_features)

   
    clients_in_specified_cluster = features[features['cluster'] == cluster_number]['client_id'].tolist()

    response_data = {
        'cluster_number': cluster_number,
        'clients': clients_in_specified_cluster
    }

    return jsonify(response_data)


if __name__ == '__main__':
    app.run(debug=True)



#1-----Function: find_optimal_clusters
#Purpose: Determines the best number of clusters for the data.
#Parameters:
#scaled_features: The standardized input data used for clustering.
#max_clusters: The maximum number of clusters to test, defaulting to 10.
#Returns: The optimal number of clusters and their silhouette scores.

#2-----API Endpoint: /cluster
#Purpose: Defines an endpoint for clustering on uploaded data.
#Loading User Data: Loads the uploaded CSV into a DataFrame.
#Analyzing Bandwidth Usage: Computes average, peak, and variance of bandwidth per client.
#Finding Peak Usage Time: Determines the hour of maximum bandwidth usage.
#Merging Features: Combines usage data and peak times into one dataset.
#Standardizing the Data: Normalizes features for clustering.
#Finding Best Clusters: Identifies the optimal number of clusters.
#Running KMeans Clustering: Categorizes clients into clusters.
#Summarizing Clusters: Calculates statistics for each cluster.
#Preparing Response: Formats summary and scores for JSON output.
#Sending Response: Returns JSON with cluster information.

#3---API Endpoint: /clients_in_cluster
#Method: POST

#Description: Accepts a CSV file and a specified cluster number, returning a list of client IDs that belong to that cluster.

#Request Parameters:

#file: CSV file containing client data.
#cluster_number: The cluster number to retrieve clients from.
#Response: Returns a JSON object containing the cluster number and a list of client IDs.



# Description : 

# Grouping clients instead of managing them individually streamlines the 
# management process, allowing businesses to focus on broader trends and 
# behaviors within each cluster. This approach simplifies oversight and 
# control of client relationships, as businesses can address groups with 
# similar usage patterns rather than handling each client separately.

# By analyzing aggregated data for these groups, organizations can make 
# informed decisions about resource allocation, ensuring that high-demand 
# clusters receive adequate support. Additionally, this strategy enables 
# the implementation of targeted engagement strategies, such as tailored 
# marketing campaigns or customized service offerings, leading to improved 
# client satisfaction and operational efficiency.





