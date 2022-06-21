
# Helm Docs GitHub Action

> GitHub Action for generation helm-docs

This is a [GitHub Action](https://developer.github.com/actions/) to generate Helm Docs for your Helm Charts. It makes use of [helm-docs](https://github.com/norwoodj/helm-docs).
This action runs in a Docker container on which helm-docs, git & bash are installed. 

## Usage

The following example will generate a README.md for the dirs "sample_chart" and "sample_chart2" recursively - meaning subfolders are also affected.<br> 
A template file is provided (README.md.gotmpl) which helm-docs can use to render the README.md file. For more information visit [helm-docs](https://github.com/norwoodj/helm-docs) Documentation page. <br>
If you wish to ignore certain dirs you can do so by providing the name of the dirs to the `ignored_dirs` varibale. Optionally you can create an .helmdocsignore file manually and add the dirs that shall be ignored directly inside it. <br> 
The variable `git_push` defines, that changes will be pushed back to the Repo. 



## Options 

The following input variable options can be configured:

|Input variable|Necessity|Description|Default|
|--------------------|--------|-----------|-------|
|`src_path`|Optional|The source path to the dir(s) to run helm-docs on. For example `.` or `some/path` | . | |
|`ignored_dirs`|Optional|Dirs you wish to ignore. Will create an .helmdocsignore file if non-existend||
|`template_file`|Optional|Provide README.md.gotmpl file to customize output. See [helm-docs](https://github.com/norwoodj/helm-docs#markdown-rendering) Markdown Rendering for more information | [default-template](https://github.com/norwoodj/helm-docs)|
|`username`|Optional|The GitHub username to associate commits made by this GitHub Action.| `github-actions-bot`|
|`email`|Optional|The email used for associating commits made by this GitHub Action| `github-actions-bot@mail.com`|
|`commit_message`|Optional|A custom git commit message| "Updating `README.md` via GithubActions (helm-docs)" |
|`git_push`|Optional|Configure whether changes shall be committed and pushed or not|false|

## Example of simple usage
```yml
name: Generate Helm Chart Documentation 
on:
  push:
jobs:
  generate-helm-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: hpi-schul-cloud/infra-tools/.github/actions/helm-docs@tf-helm-docs-v1
        with: 
          # provide list of dirs to run helm-docs on, separate by comma without a space
          src_path: sample_charts,sample_charts2
          template_file: README.md.gotmpl
          # provide name of dirs to ignore, separate by comma without a space
          ignored_dirs: dir1,dir2
          commit_message: my custom commit message
          username: sample-username
          email: sample@mail.com
          git_push: true 

```