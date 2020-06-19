#!/usr/bin/env bash
#

if [ -n "$1" -a -d "$1" ]; then
    echo -n "remove old openldap container"
    docker rm -f openldap

    docker run --detach -p 10389:389 -p 10636:636 --name openldap \
    --volume $(pwd)/${1}/50-bootstrap.ldif:/container/service/slapd/assets/config/bootstrap/ldif/50-bootstrap.ldif \
    --env LDAP_DOMAIN="${1}.org" \
    --env LDAP_BASE_DN="dc=${1},dc=org" \
    --env LDAP_ADMIN_PASSWORD="admin" \
    --env LDAP_READONLY_USER="true" \
    --env LDAP_READONLY_USER_USERNAME="readonly" \
    --env LDAP_READONLY_USER_PASSWORD="readonly" \
    --env LDAP_TLS_VERIFY_CLIENT="try" \
    osixia/openldap:1.4.0 --copy-service --loglevel debug
else
    echo "${0} <directory>"
    echo "<directory>: "
    ls  -1 -d */ | tr -d "/"
fi
