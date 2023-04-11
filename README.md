# Text Retrieval Experiment Report
## I. Important Files Introduction
- `GUI.py`: User interface
- `local_server.ipynb`: Server side
- `dataprocessing.ipynb`: Data processing related operations
- `wordseq.txt`: Word list, all using the word order in this file
- `middlesave.txt`: Intermediate save for dataframe
- `tfidf.txt`: tfidf matrix save
- `sim_article_05.txt`: Similar article ID dictionary
- `synonym.txt`: Similar words dictionary
## II. Methods
1. Data processing
    - `Completed in dataprocessing.ipynb`: Read the dataset, process the articles in the dataset by removing punctuation, tokenizing, removing stop words and low-frequency words, and standardizing words
    - `Completed in dataprocessing.ipynb`: Construct a dictionary and save it as vocab.txt
2. Retrieval and sorting
    - `Completed in local_server.ipynb's naive_articleSort()`: Retrieve and preliminarily sort the retrieved articles based on the entered search term. The preliminary sorting method is: construct a tf-idf matrix, sum the corresponding values of the keywords for each article as the relevance score, and return them in descending order of score.
    - `Completed in local_server.ipynb and GUI.py`: Build a C/S architecture, with the following specifics:
      - Since a single transfer cannot be too large, only one article title and content are transferred each time. Before transferring, the number of "how many articles need to be transferred" is sent to the client first.
      - During the operation, it was found that the sticky packet problem was prone to occur, so the size of the string to be sent was sent first using `struct.pack()`, and the receiving end used `struct.unpack()` to unpack and continue to receive the content according to this size, ensuring that the size read was strictly equal to the desired size.
3. Sorting optimization
    - `Completed in local_server.ipynb`: For the document-word TF-IDF matrix, each row is considered an article vector represented by the word's TF-IDF value, and the matrix is dimensionality-reduced to obtain low-dimensional article vectors, and then the cosine similarity between articles is calculated. Further, the HITS algorithm is used (cosine distance < 0.5 between two articles is considered as mutual association). First, use the previously mentioned `naive_articleSort()` method for preliminary sorting, then obtain the results, add the associated articles, and calculate the $authority$ value for each article in these articles, sort them in descending order to obtain the optimized retrieval results.
4. Article clustering
    - `Completed in dataprocessing.ipynb`: Cluster article vectors using `Kmeans` and compare them with the correct classification in the original dataset, calculating $Purity$, which can reach $0.95$, which is quite accurate.
5. Similar words
    - `Completed in dataprocessing.ipynb`: Use the previously obtained TF-IDF matrix to generate word vectors, obtain word vectors, calculate cosine similarity, and take words with cosine distance $<0.39$ as similar words (at this point, on average, each word has about 2 similar words) to mine similar words for each word. The results are saved as synonym.txt
6. Fuzzy matching
    - `Completed in GUI.py`: Send $1$ or $0$ to the server to indicate fuzzy matching or exact matching
    - `Completed in local_server.ipynb`: Read the saved similar words dictionary, and if $1$ is received, perform fuzzy matching by expanding similar words for the input search term. Use similar words to expand the search results set and sort them.
7. Bonus items
    - Completed in GUI.py: Optimize TKinter functionality, using "Exact Match" and "Fuzzy Match" buttons to allow users to choose for themselves