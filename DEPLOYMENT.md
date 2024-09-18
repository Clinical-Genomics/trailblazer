# Deployment guide
This includes instructions for deploying Houskeeper in the Clinical Genomics :hospital: setting. General instructions for deployment is in the [development guide][development-guide]

## Steps
When all tests are done and successful and the PR is approved by codeowners, follow these steps:

### Deploy feature branch for testing
To deploy your feature branch to test it, run
1. `trailblazer-test-deploy <branch_name>`
2. `trailblazer-test --help` or the command you want to test.

This will pull the latest image tagged with your branch from dockerhub and make it available with `trailblazer-test`.
Note that it is not necessary to paxa the environment to do this, unless you need to apply database revisions.


### Deploy to stage and production
1. Select "Squash and merge" to merge branch into default branch (master/main).
2. Append version increment value `( major | minor | patch )` in the commit message to specify what kind of release is to be created.
3. Review the details and merge the branch into master.
4. Deploy the latest version to stage and production with `trailblazer-deploy`.
5. Apply any migrations against the stage and prod databases with alembic.
    - Ensure that you have the latest revisions in your branch.
    - Ensure that you have the correct tunnels open against Hasta.
    - Ensure that you point to the correct alembic config when you apply the revisions with `alembic --config <config path>` upgrade head`
6. Take a screenshot or copy log text and post as a comment on the PR. Screenshot should include environment and that it succeeded.
7. Great job :whale2:

[development-guide]: http://www.clinicalgenomics.se/development/publish/prod/
