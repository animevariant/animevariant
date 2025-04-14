import Cycles "mo:base/ExperimentalCycles";
import Debug "mo:base/Debug";
import NFTActorClass "../nft/nft";
import Principal "mo:base/Principal";
import HashMap "mo:base/HashMap";
import List "mo:base/List";
import Iter "mo:base/Iter";


actor animeVariant {
    public query func greet(name : Text) : async Text {
    return "Hello, " # name # "!, welcome to the animeVariant canister.";
  };

  private type Listing = {
    itemOwner: Principal;
    itemPrice: Nat;
  };

  var mapOfNFTs = HashMap.HashMap<Principal, NFTActorClass.NFT>(1, Principal.equal, Principal.hash);
  var mapOfOwners = HashMap.HashMap<Principal, List.List<Principal>>(1, Principal.equal, Principal.hash);
  var mapOfListings = HashMap.HashMap<Principal, Listing>(1, Principal.equal, Principal.hash);

  //mint new nft using the nft.mo canister
  public shared(msg) func mint(imgData: [Nat8], name: Text) : async Principal {
    let owner : Principal = msg.caller;

    //add some cycles så that it actually runs on the live internet computer
    Debug.print(debug_show(Cycles.balance()));
    Cycles.add(180_500_000_000); //will come from the main canister and be allocated to the next canister that gets created.

    //create new canister containing new nft.
    let newNFT = await NFTActorClass.NFT(name, owner, imgData); 
    Debug.print(debug_show(Cycles.balance()));

    let newNFTPrincipal = await newNFT.getCanisterId();

    mapOfNFTs.put(newNFTPrincipal, newNFT);
    addToOwnershipMap(owner, newNFTPrincipal);

    return newNFTPrincipal; 

  };

  //add new nft to
  private func addToOwnershipMap(owner: Principal, nftId: Principal) {
    //find list of canister ids owned by owner
    //var ownedNFTs == mapOfOwners.get(owner); cant do this beacause the owner might be new this this data type would be null
    //the currenst safest and easiest way of dealing with options, switch statements date:5th 09 2022
    var ownedNFTs : List.List<Principal> = switch (mapOfOwners.get(owner)){
      case null List.nil<Principal>();
      case (?result) result;
    };

    //set the list to the previous version of the list plus the new nft ID
    ownedNFTs := List.push(nftId, ownedNFTs);
    mapOfOwners.put(owner, ownedNFTs);
  };

  //get list of nfts of the logged in principal(user)
  public query func getOwnedNFTs(user: Principal) : async [Principal] {
    var userNFTs : List.List<Principal> = switch(mapOfOwners.get(user)){
      case null List.nil<Principal>();
      case (?result) result;
    };
    
    return List.toArray(userNFTs);
  };

  //get list of nfts of the logged in principal(user)
  public query func getListedNFTs() : async [Principal] {
    let listedNFTIds = Iter.toArray(mapOfListings.keys()); //returns an iter of all the keys in the hashmap
    
    return listedNFTIds;
  };

  //list currently owned nfts for sale
  public shared(msg) func listItem(id: Principal, price: Nat) : async Text {
    //call the nft
    var item : NFTActorClass.NFT = switch (mapOfNFTs.get(id)){
      case null return "NFT does not exit.";
      case (?result) result;
    };
    
    //check if caller owns the nft
    let owner = await item.getOwner();
    if (Principal.equal(owner, msg.caller)){ //checks the hashmap
      let newListing : Listing = {
        itemOwner = owner;
        itemPrice = price;
      };
      mapOfListings.put(id, newListing);
      return "success";
    } else {
      return "You dont own the NFT.";
    }
  };

  //get animeVariant canister id
  public query func getanimeVariantCanisterID() : async Principal {
    return Principal.fromActor(animeVariant);
  };

  //check if an nft is listed for sale
  public query func isListed(id: Principal) : async Bool {
    if (mapOfListings.get(id) == null){
      return false;
    } else {
      return true;
    }

  };
  //get the original owner to block them from buying their stuff
  public query func getOriginalOwner(id: Principal) : async Principal {
    var listing : Listing = switch (mapOfListings.get(id)){
      case null return Principal.fromText("");
      case (?result) result;
    };
    return listing.itemOwner;
  };
 //for showing price on the discover
  public query func getListedNFTPrice(id: Principal) : async Nat {
    var listing : Listing = switch (mapOfListings.get(id)){
      case null return 0;
      case (?result) result;
    };
    return listing.itemPrice;
  };
//handle exchange between nft of buye and seller
  public shared(msg) func completePurchase(id: Principal, ownerId: Principal, newOwnerId: Principal) : async Text {
    var purchachedNFT : NFTActorClass.NFT = switch (mapOfNFTs.get(id)){
      case null return "NFT does not exist";
      case (?result) result;
    };

    let transferResult = await purchachedNFT.transferOwnership(newOwnerId);
    if (transferResult == "Success"){
      mapOfListings.delete(id);
      //previous owner nfts list
      var ownedNFTs : List.List<Principal> = switch (mapOfOwners.get(ownerId)){
        case null List.nil<Principal>();
        case (?result) result;
      };

      //filter() purchased nft from previous owner nfts list
      //loop throug each list ite and check if any matches the id of purchasednft, doesnt returns true added to new list
      ownedNFTs := List.filter(ownedNFTs, func (listItemId: Principal) : Bool {
        return listItemId != id;
      });

      //add prurchased nft to new owners list
      addToOwnershipMap(newOwnerId, id);
      return "Success";

    } else{
      return transferResult;
    }

  }

};

