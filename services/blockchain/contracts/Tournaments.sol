// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TournamentRegistry {
    struct Tournament {
        uint256 id;
        string name;
        string winner;
        string treeHash;
        uint256 timestamp;
    }

    mapping(uint256 => Tournament) private tournaments;
    uint256[] private tournamentIds;

    event TournamentRegistered(
        uint256 indexed id,
        string name,
        string winner,
        string treeHash,
        uint256 timestamp
    );

    function registerTournament(
        uint256 _id,
        string memory _name,
        string memory _winner,
        string memory _treeHash
    ) public {
        require(tournaments[_id].timestamp == 0, "Tournament with this ID already exists");

        Tournament memory newTournament = Tournament({
            id: _id,
            name: _name,
            winner: _winner,
            treeHash: _treeHash,
            timestamp: block.timestamp
        });

        tournaments[_id] = newTournament;
        tournamentIds.push(_id);

        emit TournamentRegistered(_id, _name, _winner, _treeHash, block.timestamp);
    }

    function getTournament(uint256 _id) public view returns (Tournament memory) {
        require(tournaments[_id].timestamp != 0, "Tournament not found");
        return tournaments[_id];
    }

    function getTournamentCount() public view returns (uint256) {
        return tournamentIds.length;
    }

    function getAllTournamentIds() public view returns (uint256[] memory) {
        return tournamentIds;
    }
}
