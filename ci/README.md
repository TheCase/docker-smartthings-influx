concourse.ci instructions

Install fly (link on concourse main page)

login:
```
fly -t ci login -c http://concourse.service
```

developing tests locally
```
fly -t ci execute -c ci/test.yml -i git=.
```

push up pipeline
```
./ci/set-pipeline
```

