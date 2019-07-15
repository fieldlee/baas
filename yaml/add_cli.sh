

export ORDERER_CA=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/-DomainForReplace-/orderers/-OrderIdForReplace-.-DomainForReplace-/msp/tlscacerts/tlsca.-DomainForReplace--cert.pem
export CHANNEL_NAME=-ChannelIdForReplace-

echo $ORDERER_CA && echo $CHANNEL_NAME

peer channel fetch 0 -ChannelIdForReplace-.block -o -OrderIdForReplace-.-DomainForReplace-:7050 -c $CHANNEL_NAME --tls --cafile $ORDERER_CA
peer channel join -b -ChannelIdForReplace-.block

export CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/-OrgIdForReplace-.-DomainForReplace-/peers/peer1.-OrgIdForReplace-.-DomainForReplace-/tls/ca.crt
export CORE_PEER_ADDRESS=peer1.-OrgIdForReplace-.-DomainForReplace-:-Peer1PortForReplace-

peer channel join -b -ChannelIdForReplace-.block

