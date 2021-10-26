# Github Labeler


Github Labeler is a project that extracts data, trains a model, and creates an inference endpoint to automatically tag github issues. For detailed information on how the model itself actually works, I would suggest reading the [blog](./reports/blog.md), and watching the [video](example.com).
For a brief overview, the model works by creating a binary classification model for each label. The binary classification model will be either a fastText model or a SVM model, whichever works better for that given label. During inference time an issue is passed through a different model for each possible label.

## Contents

This project contains data extraction, pre-processing training, an inference app, and openshift manifests. In order to improve models a considerable amount of work has been done to pre-train a word vector model for fastText.

### Environment Variables

The [.env.example] file shows the necessary environment variables needed for the code to run smoothly. If extracting data using the github API a github access key is required. If using ceph then the credentials are required in the .env file, and USE_CEPH should be set to 1. If not using Ceph it should be set to 0. A repo name is required in all cases. It can be either the name of a repository in the format {user/repo} or just the name of a user.

### Dataset

The dataset can be extracted in the [issue_extraction](./src/data/issue_extraction.ipynb) notebook. A github access key should be included in the .env file. It will extract either all issues from all of a user's repos or all issues from a specific repo.

### Preprocessing

After extracting the dataset, one should then run the [preprocessing notebook](./notebooks/preprocess.ipynb). Here is where the vocabulary will be built. Note that the preprocessing functions do not come from this notebook, but rather from a preprocessing [script](./src/data/preprocessing.py). The notebook is for building and saving the vocabulary, and the script is where the helper functions lie.

### Training

Once preprocessing is complete, the models can be trained. This is done in the model training [notebook](./notebooks/train_models.ipynb). This part has the most customizable features, such as making an exclusion list of users whose issues to discard, tags that aren't worth predicting, synonyms for tags, and which models you want to save.

### Manifests

Under the manifests/base folder, one can find all the essentials needed for deploying the app on openshift, namely a service, route, and deploymentconfig.

### App

The app is in the root directory, named app.py. It can be run locally or on a kubernetes cluster.

### Pre-training fastText

To pretrain our fastText model we train a Word2Vec model on general github issues. We use the [GHArchive](https://www.gharchive.org/) to extract data to train on. In order to use anything here a google BigQuery account must be made and the proper .json credentials file should be stored in the root. The first step to pre-training a vector model is to run the [vocabulary building notebook](./src/data/build_w2v_vocab.ipynb). This downloads a word vector model and reduces vocabulary as well as adds new vocabulary. Note that again, this notebook is not called for preprocessing helper functions, but the [w2v_preprocessing](./src/data/w2v_preprocessing.py) script is. Then, one can set the [pre-training notebook](./notebooks/pretrain_w2v.ipynb) to run for as long as they would like to.

### Visualizing

With a pretrained word vector model, one can then check out the [visualization notebook](fastText_viz.ipynb). I advise to look at the [gensim Word2Vec](https://radimrehurek.com/gensim/models/word2vec.html) documentation and play around with whatever you think would be interesting to look at.

## Conclusion

This is an open source project so please feel free to create issues, open pull requests, and ask questions!
