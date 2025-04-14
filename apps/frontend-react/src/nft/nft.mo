import Debug "mo:base/Debug";
import Principal "mo:base/Principal";

actor class NFT (name: Text, owner: Principal, content: [Nat8]) = this {

    // private så that they cat be changed by othe classes. only updatable within the nft itself
    private let itemName = name;
    private var nftOwner = owner;
    private let imagebytes = content;

    public query func getName() : async Text {
        return itemName;
    };
    public query func getOwner() : async Principal {
        return nftOwner;
    };
    public query func getAsset() : async [Nat8] {
        return imagebytes;
    };
    public query func getCanisterId() : async Principal {
        return Principal.fromActor(this); //this, beacause the actor nft expects input så we cant just put NFT there.
    };

    public shared(msg) func transferOwnership(newOwner: Principal) : async Text {
        if (msg.caller == nftOwner) {
            nftOwner := newOwner;
            return "Success";
        } else {
            return "Error: Not initiated by NFT Owner.";
        }
    }
};
