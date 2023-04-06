var config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    physics: {
      default: 'arcade',
      arcade: {
        gravity: { y: 300 },
        debug: false
      }
    },
    scene: {
      preload: preload,
      create: create,
      update: update
    }
  };
  
  var game = new Phaser.Game(config);
  
  var player;
  var cursors;
  var map;
  var enemies;
  
  function preload() {
    // Load game assets
    this.load.image('player', 'assets/player.png');
    this.load.image('tiles', 'assets/tiles.png');
    this.load.tilemapTiledJSON('map', 'assets/level.json');
    this.load.image('enemy', 'assets/enemy.png');
  }
  
  function create() {
    // Create the level tiles
    map = this.make.tilemap({ key: 'map' });
    var tiles = map.addTilesetImage('tiles', 'tiles');
    var platforms = map.createStaticLayer('Platforms', tiles, 0, 0);
    var hazards = map.createStaticLayer('Hazards', tiles, 0, 0);
    platforms.setCollisionByExclusion([-1]);
    hazards.setCollisionByExclusion([-1]);
  
    // Set up collisions between the player and the level tiles
    player = this.physics.add.sprite(100, 450, 'player');
    player.setBounce(0.2);
    player.setCollideWorldBounds(true);
    this.anims.create({
      key: 'left',
      frames: this.anims.generateFrameNumbers('player', { start: 0, end: 3 }),
      frameRate: 10,
      repeat: -1
    });
    this.anims.create({
      key: 'turn',
      frames: [ { key: 'player', frame: 4 } ],
      frameRate: 20
    });
    this.anims.create({
      key: 'right',
      frames: this.anims.generateFrameNumbers('player', { start: 5, end: 8 }),
      frameRate: 10,
      repeat: -1
    });
    cursors = this.input.keyboard.createCursorKeys();
    this.physics.add.collider(player, platforms);
    this.physics.add.collider(player, hazards, hitHazard, null, this);
  
    // Create the enemies
    enemies = this.physics.add.group();
    var enemy = enemies.create(500, 350, 'enemy');
    enemy.setCollideWorldBounds(true);
    enemy.setBounce(1);
    enemy.setVelocityX(100);
    enemy.setGravityY(300);
    this.physics.add.collider(player, enemies, hitEnemy, null, this);
  }
  
  function update() {
    // Player movement
    if (cursors.left.isDown) {
      player.setVelocityX(-160);
      player.anims.play('left', true);
    }
    else if (cursors.right.isDown) {
      player.setVelocityX(160);
      player.anims.play('right', true);
    }
    else {
      player.setVelocityX(0);
      player.anims.play('turn');
    }
  
    if (cursors.up.isDown && player.body.touching.down) {
      player.setVelocityY(-330);
    }
  }
  
  function hitHazard(player, hazard) {
    // Reset player position
    player.setVelocity(0, 0);
    player.setX(100);
    player.setY(450);
  }
  
  function hitEnemy(player, enemy) {
    // Knock back the player
    if (player.x < enemy.x) {
      player.setVelocityX(-300);
    }
    else {
      player.setVelocityX(300);
    }
  
    // Remove the enemy
    enemy.destroy();
  }