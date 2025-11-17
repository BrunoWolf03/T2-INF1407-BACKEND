package com.progweb.nba.controller;

import com.progweb.nba.model.Player;
import com.progweb.nba.repository.PlayerRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/players")
public class PlayerController {

    private final PlayerRepository repository;

    public PlayerController(PlayerRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    public List<Player> getAllPlayers() {
        return repository.findAll();
    }
}
