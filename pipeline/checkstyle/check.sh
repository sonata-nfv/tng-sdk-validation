#!/bin/bash
mkdir -p reports
docker run -i --rm registry.sonata-nfv.eu:5000/tng-sdk-validation pycodestyle --exclude .eggs . > reports/checkstyle-pep8.txt
echo "checkstyle result:"
cat reports/checkstyle-pep8.txt
echo "done."