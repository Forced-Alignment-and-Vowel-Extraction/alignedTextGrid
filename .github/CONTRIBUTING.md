# Contributing

Here's where you should go with any of the following:

- Bugs or feature requests
  - [Issues](https://github.com/Forced-Alignment-and-Vowel-Extraction/alignedTextGrid/issues)
- Questions, unclarity about the docs
  - [Discussions](https://github.com/Forced-Alignment-and-Vowel-Extraction/alignedTextGrid/discussions)
- Intended code contributions
  - [Issues](https://github.com/Forced-Alignment-and-Vowel-Extraction/alignedTextGrid/issues)

## Code Contributions

- Please first open an [Issue](https://github.com/Forced-Alignment-and-Vowel-Extraction/alignedTextGrid/issues) on the repository which declares your intent to contribute. 
- We're publishing from `main`, and merging pull requests into `dev` (which is set to the default branch).
- In your fork, please create an [issue branch for your work](https://docs.github.com/en/issues/tracking-your-work-with-issues/creating-a-branch-for-an-issue).
- Due to the complexity of `SequenceInterval`s, and the possibility of accidentally creating recursive operations, we're trying to maintain a high rate of code coverage. It would be ideal if you could add your own tests to `tests/`, and we may recommend some be added before we approve the pull request.
- Please send any pull requests from your issue branch onto `dev`.