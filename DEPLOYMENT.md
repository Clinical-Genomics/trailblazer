# Steps

When all tests done and successful and PR is approved, follow these steps:

1. Bump version:
    1. Merge branch to master
    1. In your local git version of this repo
        1. Checkout master by: `git checkout master`
        1. Update local branch by: `git pull origin master`
        1. Bumpversion according to specifications, eg. `bumpversion <patch/minor/major>`
        1. Push commit directly to master `git push`
        1. Push commit directly to master `git push --tag`
1. Deploy on the appropriate server:
    1. Deploy on hasta:
        1. Deploy master to stage
            1. `ssh hasta`
            1. `us`
            1. Request stage environment `paxa` and follow instructions
            1. `bash /home/proj/production/servers/resources/hasta.scilifelab.se/update-trailblazer-stage.sh master`
            1. Make sure that installation was successful
            1. `down`
        1. Deploy master to production
            1. `up`
            1. `bash /home/proj/production/servers/resources/hasta.scilifelab.se/update-trailblazer-prod.sh`
            1. Make sure that installation was successful
    1. Deploy on clinical-db:
        1. Deploy master to stage
            1. `ssh hasta`
            1. `sudo -iu hiseq.clinical`
            1. `ssh clinical-db`
            1. `us`
            1. `bash /home/hiseq.clinical/servers/resources/clinical-db.scilifelab.se/update-trailblazer-ui-stage.sh master`
            1. Make sure that installation was successful
            1. `down`
        1. Deploy master to production
            1. `up`
            1. `bash /home/hiseq.clinical/servers/resources/clinical-db.scilifelab.se/update-trailblazer-ui-prod.sh`
            1. Make sure that installation was successful
1. Take a screenshot and post as a comment on the PR. Screenshot should include environment and that it succeeded
