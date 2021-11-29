/**
 * This is the main entrypoint to your Probot app
 * @param {import('probot').Probot} app
 */
module.exports = (app) => {
  // Your code here
  app.log.info("Yay, the app was loaded!");
  const axios = require('axios')
  app.on("issues.opened", async (context) => {
    console.log(context.payload.issue.user.login)
    console.log(context.payload.issue.title)
    console.log(context.payload.issue.body)
//    const res = axios.post('http://github-labeler-ds-github-labeler.apps.smaug.na.operate-first.cloud/predict', post_input).catch()
    const res = await axios.post('http://127.0.0.1:5000/predict', {
      title: context.payload.issue.title,
      body: context.payload.issue.body,
      created_by: context.payload.issue.user.login}).catch()
    console.log(res.data)
    const output = res.data.split("\t")
    const issueComment = context.issue({
      labels: output,
    });
    return context.octokit.issues.addLabels(issueComment);
  });

  // For more information on building apps:
  // https://probot.github.io/docs/

  // To get your app running against GitHub, see:
  // https://probot.github.io/docs/development/
};
