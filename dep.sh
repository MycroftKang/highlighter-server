if [ ! -d ~/.ssh ]; then
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
fi

echo ${CUSTOM_SSH_KEY} | base64 --decode > ~/.ssh/custom_key

chmod 400 ~/.ssh/custom_key

IFS=',' ;for element in ${CUSTOM_SSH_KEY_HOSTS};
do
echo -e "Host $element\n"\
        "  IdentityFile ~/.ssh/custom_key\n"\
        "  IdentitiesOnly yes\n"\
        "  UserKnownHostsFile=/dev/null\n"\
        "  StrictHostKeyChecking no"\
        >> ~/.ssh/config
done

echo "-----> Successfully added custom SSH key"

pip install git+https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/MycroftKang/highlighter-core.git@fec30ae4b42480a0cc99438db062c8b4871c8a9f
