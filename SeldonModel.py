class SeldonModel(object):
    """
    Model template. You can load your model parameters in __init__ from a location accessible at runtime
    """

    def __init__(self):
        """
        Add any initialization parameters. These will be passed at runtime from the graph definition parameters defined in your seldondeployment kubernetes resource manifest.
        """
        load_dotenv(find_dotenv())
        self.threshold = 0.6
        self.s3_endpoint_url = os.environ["OBJECT_STORAGE_ENDPOINT_URL"]
        self.s3_access_key = os.environ["AWS_ACCESS_KEY_ID"]
        self.s3_secret_key = os.environ["AWS_SECRET_ACCESS_KEY"]
        self.s3_bucket = os.environ["OBJECT_STORAGE_BUCKET_NAME"]
        self.s3 = boto3.client(
            service_name="s3",
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key,
            endpoint_url=s3_endpoint_url,
        )
        lbllist = self.s3.get_object(Bucket=self.s3_bucket, Key="github_labeler/labellist.txt")
        with open("labellist.txt", "wb") as f:
            for i in lbllist["Body"]:
                f.write(i)
        botlist = self.s3.get_object(Bucket=self.s3_bucket, Key="github_labeler/botlist.txt")
        with open("botlist.txt", "wb") as f:
            for i in botlist["Body"]:
                f.write(i)
        with open("botlist.txt", "r") as h:
            self.bots = [bot.replace("\n", "") for bot in h.readlines()]
        with open("labellist.txt", "r") as h:
            self.labels = [lbl.replace("\n", "") for lbl in h.readlines()]

    def predict(self, X, features_names=None):
        """
        Return a prediction.

        Parameters
        ----------
        X : array-like
        feature_names : array of feature names (optional)
        """
        title, body, creator = X[0], X[1], X[2]
        if creator in self.bots:
            return ""
        ret = []
        body = body.replace("\r", "<R>").replace("\n", "<N>")
        input_ = self.title + "<SEP>" + self.body

        for lbl in self.labels:
            path = os.path.join("saved_models", lbl.replace("/", "_") + ".bin")
            model = self.s3.get_object(Bucket=self.s3_bucket, Key=path)
            with open(path, "wb") as f:
                for i in model["Body"]:
                    f.write(i)
            model = fasttext.load_model(path)
            pred, prob = model.predict(input_)
            if pred[0] == "__label__0" and prob > self.threshold:
                print(prob)
                ret.append(lbl)
            os.remove(path)

        return X