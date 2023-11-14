breed_pairing_tool.ipynb
cell 1: import helper functions
cell 2: provide ronin address, and either marketplace or inventory link to axie build (must be all 6 parts). 
cell 3: provide axieId, all axies with similar parts will be ranked in terms of compatibility, in descending order
output is c-score (compatibility score), 100 means fully compatible, 0 means not compatible (minimum is 76 for 6/6 dominant traits)

functions.py
helper functions for the notebook. 
- list of axieIds and hexadecimal genes are grabbed from GraphQL endpoints given Ronin address
- hexadecimal genes are decoded to human readable genes in Javascript
- all axie genes are compared to selected axieId, and a c-score is calculated for each axie
- axies are ranked from most to least compatible
