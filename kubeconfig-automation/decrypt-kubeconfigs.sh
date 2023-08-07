#!/bin/bash

function clear_files {
  rm -f "${password%.enc}"
  rm -f "${kubeconfigs%.enc}"
  rm -f privateKey.tmp
}

if [ -z $1 ] || [ -z $2 ] || [ -z $3 ]; then
  echo "USAGE: ./decrypt-kubeconfigs.sh <path to encrypted kubeconfigs> <path to encrypted password> <path to SSH private key>"
  exit 1
fi
kubeconfigs=$1
password=$2
sshkey=$3

for file in $kubeconfigs $password $sshkey; do
  if [ ! -f $file ]; then
    echo "File not found: $file"
    exit 1
  fi
done

if grep -q 'BEGIN RSA PRIVATE KEY' "$sshkey"; then
  openssl pkeyutl -decrypt -inkey $sshkey -in $password -out ${password%.enc} || { echo "Decrypting password failed! Are you using the correct key?"; clear_files; exit 1; }
else
  echo "Key does not start with '-----BEGIN RSA PRIVATE KEY-----'."
  echo "Trying to create a temporary copy of the key and convert it automatically."
  echo "Your original key will not be changed and the temporary key is deleted after the operation."
  echo "Enter the passphrase of the SSH-Key when asked for it."
  # Create temporary copy
  cp "$sshkey" privateKey.tmp
  # Create temporary passphrase for the converted key so that the user doesn't have to enter it 4 times
  # and there is no copy of the key without passphrase at any time
  export TMP_PASSPHRASE=$(openssl rand -hex 20)
  ssh-keygen -p -f privateKey.tmp -m pem -N "$TMP_PASSPHRASE"
  if grep -q 'BEGIN RSA PRIVATE KEY' "privateKey.tmp"; then
    echo "Temporary key converted."
  else
    echo "Couldn't convert the key. Make sure the passphrase is correct and it is a private RSA key."
    clear_files
    exit 1
  fi
  openssl pkeyutl -decrypt -passin env:TMP_PASSPHRASE -inkey privateKey.tmp -in $password -out ${password%.enc} || { echo "Decrypting password failed! Are you using the correct key?"; clear_files; exit 1; }
fi

openssl enc -d -aes-256-cbc -pbkdf2 -in $kubeconfigs -out ${kubeconfigs%.enc} -kfile ${password%.enc} || { echo "Decrypting kubeconfigs failed!"; clear_files; exit 1; }
unzip -o ${kubeconfigs%.enc} -d ~/.kube/ || { echo "Couldn't unzip kubeconfigs"; clear_files; exit 1; }
clear_files
