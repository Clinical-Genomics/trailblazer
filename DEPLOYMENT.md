# Deployment for testing
Comment on the PR with the deploy output, including the environment and that it succeeded.
Alembic revisions need to be applied from your local machine.

## Deploy CLI feature branch
1. `ssh hasta`
2. `us`
3. `trailblazer-test-deploy <feature_branch>`

## Deploy web API feature branch
1. Paxa the trailblazer stage VM.
2. Use the `Deploy branch to staging environment` Github action.

# Deploy release to production

## Deploy CLI
1. `ssh hasta`
2. `up`
3. `trailblazer-deploy <version>`

## Deploy web API
1. Use the `Deploy release to production environment` Github action.


# Steps when merging to master
When all the tests are done and successful and the PR is approved, follow these steps.

1. Select "Squash and merge" to merge branch into default branch (master/main).
2. A prompt for writing merge commit message will pop up.
3. Find the title of the pull request already pre-filled in the merge commit title, or copy and paste 
the title if not.
4. Append version increment value `( major | minor | patch )` to specify what kind of release is to be created.
5. Fill in markdown formatted changelog in merge commit comment details.
6. Review the details once again and merge the branch into master.
7. Wait for GitHub actions to process the event, bump version, create release, publish to Dockerhub and PyPi where applicable.
