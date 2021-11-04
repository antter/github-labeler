# Content

You can familiarize yourself with how the project functions by watching the video and/or reading the blog

## Video

You can find the video [here](https://www.youtube.com/watch?v=d_RFHXyGSVo).

## Blog

You can find the blog [here](./blog.md).

## Notebooks and Code

This project contains data extraction, pre-processing training, an inference app, and openshift manifests. In order to improve models a considerable amount of work has been done to pre-train a word vector model for fastText.

### Environment Variables

The .env.example file shows the necessary environment variables needed for the code to run smoothly. If extracting data using the github API a github access key is required. If using ceph then the credentials are required in the .env file, and USE_CEPH should be set to 1. If not using Ceph it should be set to 0. A repo name is required in all cases. It can be either the name of a repository in the format {user/repo} or just the name of a user.

 - [.env.example](https://github.com/aicoe-aiops/github-labeler/blob/master/.env.example)

### Dataset

The dataset can be extracted in the issue extraction notebook. A github access key should be included in the .env file. It will extract either all issues from all of a user's repos or all issues from a specific repo.

 - [Issue Extraction](https://github.com/aicoe-aiops/github-labeler/blob/master/src/data/issue_extraction.ipynb)

### Preprocessing

After extracting the dataset, one should then run the preprocessing notebook. The vocabulary will be built there. Note that the preprocessing functions do not come from this notebook, but rather from a preprocessing script. The notebook is for building and saving the vocabulary, and the script is where the helper functions lie.

 - [Preprocessing Notebook](https://github.com/aicoe-aiops/github-labeler/blob/master/notebooks/preprocess.ipynb)
 - [Script](https://github.com/aicoe-aiops/github-labeler/blob/master/src/data/preprocessing.py)

### Training

Once preprocessing is complete, the models can be trained. This is done in the model training notebook. This part has the most customizable features, such as making an exclusion list of users whose issues to discard, tags that aren't worth predicting, synonyms for tags, and which models you want to save. The models come from a model classes script that contains subclasses of already-made models.

 - [Training Notebook](https://github.com/aicoe-aiops/github-labeler/blob/master/notebooks/train_models.ipynb)
 - [Model Classes](https://github.com/aicoe-aiops/github-labeler/blob/master/notebooks/model_classes.py)

### Manifests

Under the manifests/base folder, one can find all the essentials needed for deploying the app on openshift, namely a service, route, and deploymentconfig.

 - [Manifests](https://github.com/aicoe-aiops/github-labeler/blob/master/manifests/)

### App

The app is in the root directory, named app.py. It can be run locally or on a kubernetes cluster.

- [App](https://github.com/aicoe-aiops/github-labeler/blob/master/app.py)

### Pre-training fastText

To pretrain our fastText model we train a Word2Vec model on general github issues. We use the [GHArchive](https://www.gharchive.org/) to extract data to train on. In order to use anything here a google BigQuery account must be made and the proper .json credentials file should be stored in the root. The first step to pre-training a vector model is to run the vocabulary building notebook. This downloads a word vector model and reduces vocabulary as well as adds new vocabulary. Note that again, this notebook is not called for preprocessing helper functions, but the w2v preprocessing script is. Then, one can set the pre-training notebook to run for as long as they would like to.

- [Vocabulary Building](https://github.com/aicoe-aiops/github-labeler/blob/master/src/data/build_w2v_vocab.ipynb)
- [W2V Preprocessing](https://github.com/aicoe-aiops/github-labeler/blob/master/src/data/w2v_preprocessing.py)
- [Pre-Training Notebook](https://github.com/aicoe-aiops/github-labeler/blob/master/notebooks/pretrain_w2v.ipynb)


### Visualizing

With a pretrained word vector model, one can then check out the visualization notebook. I advise to look at the [gensim Word2Vec](https://radimrehurek.com/gensim/models/word2vec.html) documentation and play around with whatever you think would be interesting to look at.

- [Visualization notebook](https://github.com/aicoe-aiops/github-labeler/blob/master/notebooks/fastText_viz.ipynb)
