# Steps

When all tests done and successful and PR is approved, follow these steps:

1. Select "Squash and merge" to merge branch into default branch (master/main).


2. A prompt for writing merge commit message will pop up.


3. Find the title of the pull request already pre-filled in the merge commit title, or copy and paste 
the title if not.


4. Append version increment value `( major | minor | patch )` to specify what kind of release is to be created.


5. Fill in markdown formatted changelog in merge commit comment details:

` ### Added `

` ### Changed `

` ### Fixed `

6. Review the details once again and merge the branch into master.


7. Wait for GitHub actions to process the event, bump version, create release, publish to Dockerhub and PyPi where applicable.

8. Deploy on the appropriate server:
    1. Deploy on hasta:
        1. Deploy master to stage
            1. `ssh hasta`
            1. `us`
            1. Request stage environment `paxa` and follow instructions
            1. ```Shell
               bash /home/proj/production/servers/resources/hasta.scilifelab.se/update-tool-stage.sh -e S_trailblazer -t trailblazer -b master -a
               ```
            1. Make sure that installation was successful
            1. `down`
        1. Deploy master to production
            1. `up`
            1. ```Shell
               bash /home/proj/production/servers/resources/hasta.scilifelab.se/update-tool-prod.sh -e P_trailblazer -t trailblazer -b master -a
               ```
            1. Make sure that installation was successful
1. Take a screenshot and post as a comment on the PR. Screenshot should include environment and that it succeeded
