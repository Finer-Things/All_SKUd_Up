# All_SKUd_Up
 A SKU correction program that uses the Levenshtein Distance. Predictions are held asside so they can be reviewed before being confirmed and memorized by the program for future corrections. 

 The Main file is a Jupyter Notebook file that runs the sku fixer algorithm. There is also a setup file called sku_fixer_setup.py and it specifies things like where to find the master sku list (with skus we want) and a list of verified sku corrections. This is also the place to specify the prediction function. 
 
 Prediction Function: The first version just used the Levenshtein distance to find the closest good sku. The current version uses the Levenshtein distance to find either the closest good sku or the closest sku that has been previously corrected (whichever is closer). 

 The current prediction algorithm is technically a k-nearest neighbours algorithm with k=1 in a 1-parameter feature space using the Levenshtein distance. A choice for k larger than 1 would not work with so many classification types and comparatively little data. 

 The first version of the program was well over 90% accurate. With some verified corrections, the current algorithm only misses a handful of skus out of 500. 
