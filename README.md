# Coin-Die-SNA

Social Network Analysis based on die studies of ancient coin collections and their findspots.

### Input Data
Die data has to be provided as two JSON files for reverse and obverse in the `rsc` directory. The content must be in the form of key-value pairs where the key is the coin identifier and the value is the respective cluster identifier, e.g. `{ coin1: cluster1, coin2: cluster1, coin3: cluster2 }`.

Findspot data is taken from the numisdata export expected in the project root directory as an CSV file named `numisdata.csv`. 

Additionally, provide the path to images of coin reverse and obverse in the `config.json` file, to view them in the web view.

If you want to see the similarity rating of two coins in a cluster with our used method to get an automated die study, Auto-Die-Studies, clone their repository and put the path to it in the config.


### Results
To view the results, run the `webserver.py` script and open the web view in your browser at `localhost:5001`.
In the "Die Data" tab, select which die study data to use for reverse and oberverse.