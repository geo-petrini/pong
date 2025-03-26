let socket = io('http://localhost:5000');

class LobbyScene extends Phaser.Scene {
    // uses https://rexrainbow.github.io/phaser3-rex-notes/docs/site/
    COLOR_MAIN = 0x505050;
    COLOR_LIGHT = 0x606060;
    COLOR_DARK = 0x707070;         
    constructor() {
        super({
            key: 'LobbyScene'
        });
    }

    preload() {
        // Precarica risorse per la lobby se necessario
        this.load.scenePlugin({
            key: 'rexuiplugin',
            // url: 'https://raw.githubusercontent.com/rexrainbow/phaser3-rex-notes/master/dist/rexuiplugin.min.js',
            // url: 'js/rexuiplugin.min.js',
            url: rexuiplugin,
            sceneKey: 'rexUI'
        });   
        this.session_id = ''    
    }

    _getInput(){

        var textArea = this.rexUI.add.textAreaInput({
            x: 400,
            y: 300,
            width: 220,
            height: 50,

            background: this.rexUI.add.roundRectangle(0, 0, 2, 2, 0, this.COLOR_MAIN),

            text: {
                background: {
                    stroke: 'white',
                    'focus.stroke': 'white',
                },

                style: {
                    fontSize: 20,
                    backgroundBottomY: 1,
                    backgroundHeight: 20,

                    'cursor.color': 'black',
                    'cursor.backgroundColor': 'white',
                },

                wrap: {
                    // wrapMode: 'word'
                }
            },

            // slider: {
            //     track: { width: 10, radius: 0, color: COLOR_DARK },
            //     thumb: { radius: 10, color: COLOR_LIGHT },
            // },

            space: {
                left: 0,
                right: 0,
                top: 0,
                bottom: 0,
                text: 10,
                header: 0,
                footer: 0,
            },

            mouseWheelScroller: {
                focus: false,
                speed: 0.1
            },

            header: this.rexUI.add.label({
                height: 30,
                orientation: 0,
                background: this.rexUI.add.roundRectangle(0, 0, 0, 0, 0, this.COLOR_DARK),
                text: this.add.text(0, 0, 'ID sessione'),
            }),

            // footer: this.rexUI.add.label({
            //     height: 30,
            //     orientation: 0,
            //     background: this.rexUI.add.roundRectangle(0, 0, 20, 20, 0, COLOR_DARK),
            //     text: this.add.text(0, 0, 'Connetti'),
            // }),

            content: this.session_id,
        })
            .layout()
            .on('textchange', function (text) {
                console.log(`Content: '${text}'`)
                this.scene.session_id = text
            })

        return textArea
    }

    _createButton(text){
        return this.rexUI.add.label({
            height: 25,
            width: 100,
            // orientation: 0,
            background: this.rexUI.add.roundRectangle(0, 0, 0, 0, 2, this.COLOR_MAIN),
            text: this.add.text(0, 0, text, {fontSize: 18}),
            align: 'center',
            // space: {top: 0, bottom: 2, left: 2, right: 2},
        })
    }

    create() {
        // var dialog = this._getDialog()
        var textArea = this._getInput()

        var buttons = this.rexUI.add.buttons({
            // buttons: [textArea.childrenMap['footer'] ]
            x: 400+170,
            y: 300,
            orientation: 'y',
            buttons:[
                this._createButton('Crea'),
                this.rexUI.add.space(),
                this._createButton('Connetti')
            ]
        }).layout()
        // .drawBounds(this.add.graphics(), 0xff0000)

        buttons
        .on('button.click', function (button, index, pointer, event) {
            // print.text += `Click button-${button.text}\n`;
            console.debug(`Pointer-click: ${button.text}`)
            button.scaleYoyo(500, 1.2);
            buttons.setButtonEnable(false)
            setTimeout(() => {
                buttons.setButtonEnable(true)
            }, 250);
            if (button.text == 'Crea'){
                socket.emit('createSession', { session_id: this.scene.session_id });
            }
            if (button.text == 'Connetti'){
                socket.emit('joinSession', { session_id: this.scene.session_id }); 
            }
        })
        .on('button.out', function (button) {
            console.debug(`Pointer-out: ${button.text}`)
            // button.stroke = 'black'
        })
        .on('button.over', function (button) {
            console.debug(`Pointer-over: ${button.text}`)
            // button.background.stroke = 'white'
        })
        .on('button.down', function (button) {
            console.debug(`Pointer-down: ${button.text}`)
        })
        .on('button.up', function (button) {
            console.debug(`Pointer-up: ${button.text}`)
        })

        // Gestire la risposta dal server quando la sessione viene creata
        socket.on('sessionCreated', (response) => {
            if (response && response.session_id) {this.startGame(response.session_id)}
        });

        // Gestire la risposta dal server quando si è uniti alla sessione
        socket.on('sessionJoined', (response) => {
            if (response && response.session_id) {this.startGame(response.session_id)}
        });
        
        // Gestire gli errori
        socket.on('error', (error) => {
            alert(error.message);  // Mostra un errore se la sessione non è trovata
        });
        
    }

    startGame(session_id) {
        setTimeout(() => {
            this.scene.start('GameScene', { sessionId: session_id });
        }, 300);
    }
}

class GameScene extends Phaser.Scene {

    constructor(test) {
        super({
            key: 'GameScene'
        });
    }
    init(data){
        this.paddleLeft
        this.paddleRight
        this.ball
        this.cursors
        this.keys;
        this.gameState = {};
        this.paddleSide = 'spectator'; // Predefinito: spettatore
        this.sessionId = data.sessionId;

        this.paddleInfo = document.getElementById('paddle-info');
        this.sessionInfo = document.getElementById('session-info');
    }

    preload () {
        const graphics = this.add.graphics();
        graphics.fillStyle(0xffffff, 1);
    
        const paddleTexture = this.textures.createCanvas('paddle', 10, 100);
        graphics.fillRect(0, 0, 10, 100);
        graphics.generateTexture('paddle', 10, 100);
    
        const ballTexture = this.textures.createCanvas('ball', 10, 10);
        graphics.clear();
        graphics.fillStyle(0xffffff, 1);
        graphics.fillRect(0, 0, 10, 10);
        graphics.generateTexture('ball', 10, 10);
    }
    
    create() {
        this.paddleLeft = this.physics.add.image(50, config.height / 2, 'paddle').setImmovable(true);
        this.paddleRight = this.physics.add.image(config.width - 50, config.height / 2, 'paddle').setImmovable(true);
        this.ball = this.physics.add.image(config.width / 2, config.height / 2, 'ball').setCollideWorldBounds(true).setBounce(1);
    
        // ball.setVelocity(200, 200);
    
        this.paddleLeft.body.collideWorldBounds = true;
        this.paddleRight.body.collideWorldBounds = true;
    
        this.physics.add.collider(this.ball, this.paddleLeft);
        this.physics.add.collider(this.ball, this.paddleRight);
    
        this.cursors = this.input.keyboard.createCursorKeys();
        this.keys = this.input.keyboard.addKeys('W,S');
    
        // Connect to the Flask server via Socket.IO
    
        socket.on('connect', () => {
            console.log('✅ Connesso al server Pong');
        });
    
        // Riceve l'assegnazione del paddle (sinistra, destra o spettatore)
        socket.on('assignPaddle', (data) => {
            this.paddleSide = data.paddle;
            this.updatePaddleInfo();
            console.log(`🎮 Paddle assegnato: ${this.paddleSide}`);
        });
    
        socket.on('gameState', (state) => {
            this.gameState = state;
            this.updateGameObjects();
        });
    }
    
    update() {
        if (this.paddleSide === 'spectator') return; // Spettatori non controllano i paddle
        let paddleVelocity = 0;
    
        // Controllo del paddle sinistro (W e S)
        if (this.paddleSide === 'left') {
            if (keys.W.isDown) paddleVelocity = -300;
            else if (keys.S.isDown) paddleVelocity = 300;
        }
    
        // Controllo del paddle destro (Freccia Su e Giù)
        if (this.paddleSide === 'right') {
            if (cursors.up.isDown) paddleVelocity = -300;
            else if (cursors.down.isDown) paddleVelocity = 300;
        }
    
        // Movimento del paddle locale
        let currentPaddle = paddleSide === 'left' ? this.paddleLeft : this.paddleRight;
        currentPaddle.body.setVelocityY(paddleVelocity);
    
        // Invia aggiornamento solo se la posizione cambia
        if (this.paddleSide === 'left' && currentPaddle.y !== this.gameState.paddleLeftY) {
            socket.emit('updatePaddle', { paddle: 'left', paddleY: currentPaddle.y });
        } else if (this.paddleSide === 'right' && currentPaddle.y !== this.gameState.paddleRightY) {
            socket.emit('updatePaddle', { paddle: 'right', paddleY: currentPaddle.y });
        }
    
        // Sincronizza sempre paddle e palla con il server
        this.updateGameObjects();
    }
    
    updateGameObjects() {
        if (!this.gameState) return;
    
        // muovi il paddle dell'avversario secondo quanto ricevuto dal server
        if (this.paddleSide === 'left') {
            this.paddleRight.y = this.gameState.paddleRightY;
        }
        if (this.paddleSide === 'right') {
            this.paddleLeft.y = this.gameState.paddleLeftY;
        }
    
        // muove la palla secondo quanto ricevuto dal server
        this.ball.x = this.gameState.ballX;
        this.ball.y = this.gameState.ballY;
    }
    
    updatePaddleInfo() {
        if (this.paddleSide === 'left') {
            this.paddleInfo.textContent = "🎮 Stai controllando: Sinistra";
        } else if (paddleSide === 'right') {
            this.paddleInfo.textContent = "🎮 Stai controllando: Destra";
        } else {
            this.paddleInfo.textContent = "👀 Stai osservando la partita";
        }
    }    
}

const config = {
    // For more settings see <https://github.com/photonstorm/phaser/blob/master/src/boot/Config.js>
    type: Phaser.AUTO,
    pixelArt: true,
    roundPixels: true,
    parent: 'phaser-content',
    width: 800,
    height: 600,
    physics: {
        default: 'arcade',
        arcade: {
            debug: false
        }
    },
    scene: [
        LobbyScene,
        GameScene,
    ]
};

const game = new Phaser.Game(config); // eslint-disable-line no-unused-vars
