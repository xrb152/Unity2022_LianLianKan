using UnityEngine;
using System.Collections;
//using UnityEngine.Advertisements;
using System;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using SimpleJSON;
using System.Collections.Generic;

public class GameStatic : MonoBehaviour {
	public static Map map;
	public Map _map;
	public static LogicLevel logicLevel;
	public  LogicLevel _logicLevel;
	public static ItemController itemRandom;
	public  ItemController _itemRandom;
	public static ItemController itemHint;
	public  ItemController _itemHint;
	public static ItemController itemEnergy;
	public  ItemController _itemEnergy;
	public static TimeBar timeBar;
	public  TimeBar _timeBar;
	public static EnergyBar energyBar;
	public  EnergyBar _energyBar;
	public static PauseBar pauseBar;
	public  PauseBar _pauseBar;
	public static MessagePopup messagePopup;
	public  MessagePopup _messagePopup;
	public  GameObject _store;
	public static GameObject store;
	public  GameObject _toastPool;
	public static PlayerInfo playerInfo;
	public  PlayerInfo _playerInfo;
	public static GameObject toastPool;
	public static Text txtAddingScore;
	public Text _txtAddingScore;
	public  RectTransform _canvas;
	public static RectTransform canvas;

	public  GameObject _firstObiUI;
	public static GameObject firstObiUI;
	public static RatePopup ratePopup;
	public RatePopup _ratePopup;
	public static MainMenu mainMenu;
	public MainMenu _mainMenu;
	public static StoreController2 storeController;
	public StoreController2 _storeController;
	public static MessagePopup recoverLifePopup;
	public  MessagePopup _recoverLifePopup;



	public static InputName inputName;
	public InputName _inputName;

	public bool IsShowRanking = false;
	public static bool canShowRatePopup = false;

	public static int currentMode = Const.GAME_MODE_NORMAL; // currentMode = 0 -> normal, currentMode = 1: hard1 (8 level), currentMode = 2: hard2 (40 level)
	public static int currentLevel = 1;
	public static int currentHint = 10;
	public static int currentRandom = 10;
	// 关卡通关奖励的提示/洗牌：先记在这里，等下一关 setLevel 重算道具时一起加进去，
	// 否则「每关重置为关卡定量」会把刚发的奖励直接冲掉。
	public static int pendingHint = 0;
	public static int pendingRandom = 0;
	public static int currentScore = 0;
	public static int countPlayAgain = 0;
	public static int maxLevel;
	public static JSONNode mapData = null;
	public static int coin_need_to_recover = 5;
//	public static bool IsConnectedGooglePlayService = Social.localUser.authenticated;
	public static bool IsConnectedGooglePlayService = false;


	// Use this for initialization
	void Start () {
		map = _map;
		logicLevel = _logicLevel;
		itemEnergy = _itemEnergy;
		itemRandom = _itemRandom;
		itemHint = _itemHint;
		timeBar = _timeBar;
		energyBar = _energyBar;
		pauseBar = _pauseBar;
		messagePopup = _messagePopup;
		recoverLifePopup = _recoverLifePopup;
		store = _store;
		toastPool = _toastPool;
		GameConfig.num_level = Save.getDownloadedLevel ();
		canvas = _canvas;
		firstObiUI = _firstObiUI;
		txtAddingScore = _txtAddingScore;

		ratePopup = _ratePopup;
		mainMenu = _mainMenu;
		// 每次进入场景先结算离线体力恢复
		ItemController.applyEnergyRecovery ();
		if (GameObject.Find ("Store") != null) {
			_storeController = GameObject.Find ("Store").GetComponent<StoreController2> ();
		}
		storeController = _storeController;
		playerInfo = _playerInfo;
		
		inputName = _inputName;
		//loadAds ();
		//if (SceneManager.GetActiveScene ().name == "Main" && Save.getTutorialStatus() != 0 ) {
		//	//google play service
		//	PlayGamesPlatform.Activate ();
		//	PlayGamesPlatform.DebugLogEnabled = true;
		//	//ConnectToGooglePlayService ();
		//}
		//if (GSM.isLogin && (GSM.userData ["userName"] == null || GSM.userData ["userName"].ToString().Equals(""))) {
		//	GameStatic.inputName.show ();
		//}
	}

	void Update(){
		#if !UNITY_IOS
			if (Input.GetKey (KeyCode.Escape)) {
				if (SceneManager.GetActiveScene ().name.Equals (StringUtils.scene_level)||SceneManager.GetActiveScene ().name.Equals (StringUtils.scene_play_tutorial)) {
					SceneManager.LoadScene (StringUtils.scene_main);
				}
				if (SceneManager.GetActiveScene ().name.Equals (StringUtils.scene_online_menu)) {
					LoadingScene.loadingScreen.loadMain ();
				}
				if (SceneManager.GetActiveScene ().name.Equals (StringUtils.scene_main)) {
					_mainMenu.QuitGame ();
				}
			}
		// }
		#endif
		if (GameConfig.DEBUG_KEY) {
			if (Input.GetKey (KeyCode.C)) {
				PlayerPrefs.DeleteAll ();
				PlayerPrefs.Save ();
				Debug.Log ("Clear cache");
			}
			if (Input.GetKey (KeyCode.M)) {
				RedirectController. REDIRECT_BY_EVENT = Const.REDIRECT_OPEN_MESSAGE;
			}
			if (Input.GetKey (KeyCode.T)) {
				Save.saveHighScore (100);
			}
		}

		//if (IsShowRanking) {
		//	if (SceneManager.GetActiveScene ().name.Equals (StringUtils.scene_main)) {
		//		IsShowRanking = false;
		//		_mainMenu.showLeaderBoard ();
		//	}
		//}
	}

	//public static void postScore(int score) {
	//	if(currentMode == Const.GAME_MODE_EVENT) return;
	//	string leaderboardStr = PikachuRankingResource.leaderboard_pikachu_ranking_normal;
	//	if (currentMode == Const.GAME_MODE_HARD1) {
	//		leaderboardStr = PikachuRankingResource.leaderboard_pikachu_ranking_hard_1;
	//	} else if (currentMode == Const.GAME_MODE_HARD2) {
	//		leaderboardStr = PikachuRankingResource.leaderboard_pikachu_ranking_hard_2;
	//	}
	//	Social.ReportScore (score, leaderboardStr, success => {
	//		CustomDebug.Log ("Post score to mode :: " + currentMode + " :: " + success);
	//		CustomDebug.Log ("Post score " + score + " :: " + success);
	//	});
	//}

	//public void debugPostScore() {
	//	int score = UnityEngine.Random.Range (0, 1000);
	//	int currentMode = UnityEngine.Random.Range (0, 3);
	//	string leaderboardStr = PikachuRankingResource.leaderboard_pikachu_ranking_normal;
	//	if (currentMode == Const.GAME_MODE_HARD1) {
	//		leaderboardStr = PikachuRankingResource.leaderboard_pikachu_ranking_hard_1;
	//	} else if (currentMode == Const.GAME_MODE_HARD2) {
	//		leaderboardStr = PikachuRankingResource.leaderboard_pikachu_ranking_hard_2;
	//	}
	//	Social.ReportScore (score, leaderboardStr, success => {
	//		ToastManager.showToast("Post score " + score + " :: " + success);
	//	});
	//}
	//public static void ConnectToGooglePlayService() {
	//	if (!IsConnectedGooglePlayService) {
	//		Social.localUser.Authenticate ((bool success) => {
	//			CustomDebug.Log ("Connected to google play service :: " + success);
	//			IsConnectedGooglePlayService = success;
	//		});
	//	}
	//}

    public static void handleQuitApp()
    {
        // PushNotification.instance.pushRecoverEnergyNotification();
        if (Application.platform == RuntimePlatform.Android)
        {
            Application.Quit();
        }
    }

    public void test(){
		map.test ();
	}

    //public static void loadAds(){
    //}

    //private void RequestBanner()
    //{
    //}

    public void showAds()
    {
  
    }

    public static void ShowAds()
    {
     
    }

    public static void updateItemNumber(){
		if (itemHint != null) {
			itemHint.updateItemUI ();
		}	
		if (itemRandom != null) {
			itemRandom.updateItemUI ();
		}	
		if (itemEnergy != null) {
			itemEnergy.updateItemUI ();
		}
	}

	//public void openFacebookPage(){
	//	Application.OpenURL("http://www.facebook.com/pukachionline#");
	//}

	public static void openStore(){
		#if UNITY_ANDROID
		Application.OpenURL("http://play.google.com/store/apps/details?id=com.minigameshouse.pikachuclassic");
		#else
		Application.OpenURL("http://itunes.apple.com/vn/app/pukachi-online/id1068833233?mt=8");
		#endif
	}

	public void openPage(){
		//Application.OpenURL(GameConfig.link_web);
	}

	public static void openLink(string link){
		Application.OpenURL(link);
	}

	public void inviteFriend(){
	}

	// public static void loadNewGame(int mode) {
	// 	if (mode == Const.GAME_MODE_EVENT) {
	// 		loadNewGameEvent();
	// 	} else {
	// 		loadNewGameRegular(mode);
	// 	}
	// }

//	public static void loadOldGame(int mode) {
//		if (mode == Const.GAME_MODE_EVENT) {
//			loadOldGameEvent();
//		} else {
//			loadOldGameRegular();
//		}
//	}

	public static void saveGame() {
		if (currentMode == Const.GAME_MODE_EVENT) {
			saveGameEvent();
		} else {
			saveGameRegular();
		}
	}

	public static void saveGameTime() {
		if (currentMode == Const.GAME_MODE_EVENT) {
			saveGameEventTime();
		} else {
			saveGameRegularTime();
		}
	}

	public static void saveGameWithoutMap() {
		if (currentMode == Const.GAME_MODE_EVENT) {
			saveGameEventWithoutMap();
		} else {
			saveGameRegularWithoutMap();
		}
	}

	public static void saveGameForReplay() {
		if (currentMode == Const.GAME_MODE_EVENT) {
			saveGameEventForReplay();
		} else {
			saveGameRegularForReplay();
		}
	}

	public static void endGame() {
		if (currentMode == Const.GAME_MODE_EVENT) {
			endGameEvent();
		} else {
			endGameRegular();
		}
	}

	// for regular game
	public static bool loadNewGameRegular(int mode) {
		currentMode = mode;
		// 每开始新的一局扣体力；不足时直接返回，不重置局内进度
		if (!ItemController.useEnergyToStartRun ())
			return false;
		currentLevel = 1;
		currentScore = 0;
		countPlayAgain = 0;
		mapData = null;
		if (currentMode == Const.GAME_MODE_HARD1) {
			maxLevel = GameConfig.num_level_hard1;
			currentHint = GameConfig.default_num_hint_hard1;
			currentRandom = GameConfig.default_num_random_hard1;
		} else if (currentMode == Const.GAME_MODE_HARD2) {
			maxLevel = GameConfig.num_level_hard2;
			currentHint = GameConfig.default_num_hint_hard2;
			currentRandom = GameConfig.default_num_random_hard2;
		} else {
			maxLevel = GameConfig.num_level;
			currentHint = GameConfig.default_num_hint_normal;
			currentRandom = GameConfig.default_num_random_normal;
		}
		Save.saveLevel (1);
		Save.saveScore (0);
		Save.saveMapData("");
		Save.saveGameMode (mode);
		Save.setCountPlayAgain(0);
		// 新开一局：清空上一局残留的关卡奖励
		pendingHint = 0;
		pendingRandom = 0;
		ItemController.setHintItem (currentHint);
		ItemController.setRandomItem (currentRandom);
		SoundSystem.ins.play_music_back ();
		return true;
	}

	/// <summary>体力不足时的统一处理：打开商店面板让玩家用钻石买体力。</summary>
	public static void handleNotEnoughEnergy() {
		openStorePanel ();
	}

	/// <summary>打开商店面板（主界面 / 战斗界面通用，找不到引用时按类型查找）。</summary>
	public static void openStorePanel() {
		GameObject go = store;
		if (go == null) {
			StoreController2[] list = Resources.FindObjectsOfTypeAll<StoreController2> ();
			for (int i = 0; i < list.Length; i++) {
				StoreController2 sc = list [i];
				if (sc != null && sc.gameObject.scene.IsValid ()) {
					go = sc.gameObject;
					break;
				}
			}
		}
		if (go == null) {
			CustomDebug.Log ("openStorePanel :: store not found");
			return;
		}
		Popup popup = go.GetComponent<Popup> ();
		if (popup != null) {
			popup.showPopup ();
		} else if (go.transform.parent != null) {
			go.transform.parent.gameObject.SetActive (true);
		} else {
			go.SetActive (true);
		}
	}

	public static void loadOldGameRegular() {
		currentMode = Save.getGameMode ();
		currentLevel = Save.getCurrentLevel ();
		currentScore = Save.getCurrentScore ();
		currentHint = ItemController.getNumHintItem ();
		currentRandom = ItemController.getNumRandomItem ();
		countPlayAgain = Save.getCountPlayAgain();
		//maxLevel = currentMode == 1 ? GameConfig.num_level_hard : GameConfig.num_level;
		if (currentMode == Const.GAME_MODE_HARD1) {
			maxLevel = GameConfig.num_level_hard1;
		} else if (currentMode == Const.GAME_MODE_HARD2) {
			maxLevel = GameConfig.num_level_hard2;
		} else {
			maxLevel = GameConfig.num_level;
		}
		if (Save.getMapData() != "") {
			mapData = JSON.Parse (Save.getMapData ());
		}
		SoundSystem.ins.play_music_back ();
	}

	public static void saveGameRegular() {
		JSONClass data = new JSONClass ();
		JSONClass mapData = new JSONClass ();
		JSONClass mapFrozenData = new JSONClass ();
		JSONArray listAutoGens = new JSONArray ();
		for (int i = 1; i < map.row; i++) {
			for (int j = 1; j < map.col; j++) {
				mapData [i + ""] [j + ""] = new JSONData(map.MAP [i] [j]);
				mapFrozenData [i + ""] [j + ""] = new JSONData (map.MAP_FROZEN [i] [j]);
				if (map.MAP_FROZEN [i] [j] == Const.FROZEN_FIXED_ID) {
					Debug.Log("frozen :: " + i + " - " + j);
				}
			}
		}
		for (int i = 0; i < map.listAutoGens.Count; i++) {
			AutoGenController autoGen = (AutoGenController) map.listAutoGens [i];
			JSONClass autoGenData = new JSONClass ();
			autoGenData ["current_time"] = new JSONData (autoGen.getCurrentTime ());
			autoGenData ["current_clock_time"] = new JSONData (autoGen.clockCountDown.getCurrentTime());
			autoGenData ["type"] = new JSONData (autoGen.autoGenData.type);
			autoGenData ["time_wait"] = new JSONData (autoGen.autoGenData.timeWait);
			autoGenData ["time_run"] = new JSONData (autoGen.autoGenData.timeRun);
			autoGenData ["row"] = new JSONData (autoGen.pos.R);
			autoGenData ["col"] = new JSONData (autoGen.pos.C);
			listAutoGens.Add (autoGenData);
		}
		data ["map_data"] = mapData;
		data ["map_frozen_data"] = mapFrozenData;
		data ["auto_gen"] = listAutoGens;
		data ["current_time"] = new JSONData(map.logicLevel.timeBar.getTimeRemain ());
		Debug.Log ("SAVE GAME :: " + data.ToString ());
		Save.saveMapData (data.ToString ());
		Save.saveLevel (currentLevel);
		Save.saveScore (currentScore);
		Save.setContinueStatus(1);
	}

	public static void saveGameRegularTime() {
		if (Save.getMapData() != "") {
			JSONNode mapData = JSON.Parse (Save.getMapData ());
			mapData ["current_time"] = new JSONData(map.logicLevel.timeBar.getTimeRemain ());
			Save.saveMapData (mapData.ToString ());
		}
	}

	public static void saveGameRegularWithoutMap() {
		currentLevel ++;
		Save.saveLevel (currentLevel);
		Save.saveScore (currentScore);
		Save.saveMapData ("");
		mapData = null;
	}

	public static void saveGameRegularForReplay() {
		// 复活补偿直接加进当前关的道具池：Replay() 是原地重建地图、不重算关卡定量，所以加完就生效
		ItemController.addHintItem (GameConfig.num_hint_bonus);
		ItemController.addRandomItem (GameConfig.num_random_bonus);
		currentHint = ItemController.getNumHintItem ();
		currentRandom = ItemController.getNumRandomItem ();
		countPlayAgain++;
		Save.saveLevel (currentLevel);
		Save.saveScore (currentScore);
		Save.saveMapData ("");
		Save.setCountPlayAgain(countPlayAgain);
		mapData = null;
	}

	public static void endGameRegular() {
		Save.saveMapData("");
		Save.setContinueStatus(0);
		Save.saveHighScore(currentScore);
		//postScore (currentScore);
		mapData = null;
	}

	//for event
	public static void loadNewGameEvent() {
		currentMode = Const.GAME_MODE_EVENT;
		currentLevel = 1;
		currentScore = 0;
		countPlayAgain = 0;
		mapData = null;
		maxLevel = GameConfig.num_level_event;
		currentHint = GameConfig.default_num_hint_event;
		currentRandom = GameConfig.default_num_random_event;
		Save.saveLevelEvent (1);
		Save.saveScoreEvent (0);
		Save.saveMapDataEvent("");
		// Save.saveGameMode (mode);
		Save.setCountPlayEventAgain(0);
		pendingHint = 0;
		pendingRandom = 0;
		ItemController.setHintItem (currentHint);
		ItemController.setRandomItem (currentRandom);
		SoundSystem.ins.play_music_back ();
	}

	public static void loadOldGameEvent() {
		currentMode = Const.GAME_MODE_EVENT;
		currentLevel = Save.getCurrentLevelEvent ();
		currentScore = Save.getCurrentScoreEvent ();
		currentHint = ItemController.getNumHintItem ();
		currentRandom = ItemController.getNumRandomItem ();
		countPlayAgain = Save.getCountPlayEventAgain();
		maxLevel = GameConfig.num_level_event;
		//maxLevel = currentMode == 1 ? GameConfig.num_level_hard : GameConfig.num_level;
		// if (currentMode == Const.GAME_MODE_HARD1) {
		// 	maxLevel = GameConfig.num_level_hard1;
		// } else if (currentMode == Const.GAME_MODE_HARD2) {
		// 	maxLevel = GameConfig.num_level_hard2;
		// } else {
		// 	maxLevel = GameConfig.num_level;
		// }
		if (Save.getMapDataEvent() != "") {
			mapData = JSON.Parse (Save.getMapDataEvent ());
		}
		SoundSystem.ins.play_music_back ();
	}

	public static void saveGameEvent() {
		JSONClass data = new JSONClass ();
		JSONClass mapData = new JSONClass ();
		JSONClass mapFrozenData = new JSONClass ();
		JSONArray listAutoGens = new JSONArray ();
		for (int i = 1; i < map.row; i++) {
			for (int j = 1; j < map.col; j++) {
				mapData [i + ""] [j + ""] = new JSONData(map.MAP [i] [j]);
				mapFrozenData [i + ""] [j + ""] = new JSONData (map.MAP_FROZEN [i] [j]);
				if (map.MAP_FROZEN [i] [j] == Const.FROZEN_FIXED_ID) {
					Debug.Log("frozen :: " + i + " - " + j);
				}
			}
		}
		for (int i = 0; i < map.listAutoGens.Count; i++) {
			AutoGenController autoGen = (AutoGenController) map.listAutoGens [i];
			JSONClass autoGenData = new JSONClass ();
			autoGenData ["current_time"] = new JSONData (autoGen.getCurrentTime ());
			autoGenData ["current_clock_time"] = new JSONData (autoGen.clockCountDown.getCurrentTime());
			autoGenData ["type"] = new JSONData (autoGen.autoGenData.type);
			autoGenData ["time_wait"] = new JSONData (autoGen.autoGenData.timeWait);
			autoGenData ["time_run"] = new JSONData (autoGen.autoGenData.timeRun);
			autoGenData ["row"] = new JSONData (autoGen.pos.R);
			autoGenData ["col"] = new JSONData (autoGen.pos.C);
			listAutoGens.Add (autoGenData);
		}
		data ["map_data"] = mapData;
		data ["map_frozen_data"] = mapFrozenData;
		data ["auto_gen"] = listAutoGens;
		data ["current_time"] = new JSONData(map.logicLevel.timeBar.getTimeRemain ());
		Debug.Log ("SAVE GAME :: " + data.ToString ());
		Save.saveMapDataEvent (data.ToString ());
		Save.saveLevelEvent (currentLevel);
		Save.saveScoreEvent (currentScore);
		Save.setContinueEventStatus(1);
	}

	public static void saveGameEventTime() {
		if (Save.getMapDataEvent() != "") {
			JSONNode mapData = JSON.Parse (Save.getMapDataEvent ());
			mapData ["current_time"] = new JSONData(map.logicLevel.timeBar.getTimeRemain ());
			Save.saveMapDataEvent (mapData.ToString ());
		}
	}

	public static void saveGameEventWithoutMap() {
		currentLevel ++;
		Save.saveLevelEvent (currentLevel);
		Save.saveScoreEvent (currentScore);
		Save.saveMapDataEvent ("");
		mapData = null;
	}

	public static void saveGameEventForReplay() {
		ItemController.addHintItem (GameConfig.num_hint_bonus);
		ItemController.addRandomItem (GameConfig.num_random_bonus);
		currentHint = ItemController.getNumHintItem ();
		currentRandom = ItemController.getNumRandomItem ();
		countPlayAgain++;
		Save.saveLevelEvent (currentLevel);
		Save.saveScoreEvent (currentScore);
		Save.saveMapDataEvent ("");
		Save.setCountPlayEventAgain(countPlayAgain);
		mapData = null;
	}

	public static void endGameEvent() {
		Save.saveMapDataEvent("");
		Save.setContinueEventStatus(0);
//		Save.saveHighScoreEvent(currentScore);
		// postScore (currentScore);
		mapData = null;
	}

	public void resetHighScore() {
		Save.saveHighScore(0);
		ToastManager.showToast("最高分已重置");
	}

	public void debugNextLevel() {
		if (GameConfig.DEBUG_KEY) {
			map.nextLevel();
		}
	}

	public void showRanking() {
		IsShowRanking = true;
	}

	//=================log player level=================//
	public static void logLevel(int mode, int hintRemain, int randomRemain, int level, int status, int currentScore, bool localOnly) {
		string statusName = status > 0 ? "Pass" : "Fail";
		JSONArray listLevelData = getLogLevelData ();
		JSONClass levelData = new JSONClass();
		levelData.Add ("mode", new JSONData (mode));
		levelData.Add ("current_score", new JSONData (currentScore));
		levelData.Add ("hint_remain", new JSONData (hintRemain));
		levelData.Add ("random_remain", new JSONData (randomRemain));
		levelData.Add ("level", new JSONData (level));
		levelData.Add ("status", new JSONData (status));
		levelData.Add ("status_name", new JSONData (statusName));
		listLevelData.Add (levelData);
		Debug.Log ("logLevel :: " + listLevelData.ToString());
		PlayerPrefs.SetString ("log_level_data", listLevelData.ToString());
		PlayerPrefs.Save ();
	}

	public static JSONArray getLogLevelData() {
		JSONArray logLevelData = new JSONArray ();
		string log_level_data = PlayerPrefs.GetString("log_level_data", "");
		if (log_level_data != null && !log_level_data.Equals("")) {
			logLevelData = JSON.Parse(log_level_data).AsArray;
			return logLevelData;
		}
		return logLevelData;
	}

	public static void clearLogLevelData() {
		PlayerPrefs.DeleteKey ("log_level_data");
		PlayerPrefs.Save ();
	}

	//===================log player use coin===================//
	public static void logUseCoin(int mode, int level, int coin_use, int coin_remain, bool localOnly) {
		JSONArray listUseCoinData = getLogUseCoinData ();
		JSONClass useCoinData = new JSONClass();
		useCoinData.Add ("mode", new JSONData (mode));
		useCoinData.Add ("level", new JSONData (level));
		useCoinData.Add ("coin_use", new JSONData (coin_use));
		useCoinData.Add ("coin_remain", new JSONData (coin_remain));
		listUseCoinData.Add (useCoinData);
		PlayerPrefs.SetString ("log_use_coin_data", listUseCoinData.ToString());
		PlayerPrefs.Save ();
	}

	public static JSONArray getLogUseCoinData() {
		JSONArray logUseCoinData = new JSONArray ();
		string log_use_coin_data = PlayerPrefs.GetString("log_use_coin_data", "");
		if (log_use_coin_data != null && !log_use_coin_data.Equals("")) {
			logUseCoinData = JSON.Parse(log_use_coin_data).AsArray;
			return logUseCoinData;
		}
		return logUseCoinData;
	}

	public static void clearLogUseCoinData() {
		PlayerPrefs.DeleteKey ("log_use_coin_data");
		PlayerPrefs.Save ();
	}

	public static bool checkEnoughCoinToRecover() {
		int coinNeed = GameStatic.coin_need_to_recover;
		int currentCoin = Save.getPlayerCoin();
		if (currentCoin >= coinNeed) {
			return true;
		}
		return false;
	}

	public static int getCoinNeedToRecover() {
		if (countPlayAgain == 0) {
			if (Save.getPlayerCoin () == 0)
				return GameConfig.coin_revive_when_0;
			else if (Save.getPlayerCoin () < GameConfig.num_coin_recover_life_base) {
				return Save.getPlayerCoin ();
			}
		}
		return (countPlayAgain + 1) * GameConfig.num_coin_recover_life_base;
	}

	//=================log player buy coin=====================//
	public static void logBuyCoin(string pack_id, int coin_add, int player_coin,string transactionID, bool localOnly=false) {
		JSONArray listBuyCoinData = getLogBuyCoinData ();
		JSONClass buyCoinData = new JSONClass();
		buyCoinData.Add ("pack_id", new JSONData (pack_id));
		buyCoinData.Add ("coin_add", new JSONData (coin_add));
		buyCoinData.Add ("player_coin", new JSONData (player_coin));
		buyCoinData.Add ("transaction_id", new JSONData (transactionID));
		listBuyCoinData.Add (buyCoinData);
		PlayerPrefs.SetString ("log_buy_coin_data", listBuyCoinData.ToString());
		PlayerPrefs.Save ();
	}

	public static JSONArray getLogBuyCoinData() {
		JSONArray logBuyCoinData = new JSONArray ();
		string log_buy_coin_data = PlayerPrefs.GetString("log_buy_coin_data", "");
		if (log_buy_coin_data != null && !log_buy_coin_data.Equals("")) {
			logBuyCoinData = JSON.Parse(log_buy_coin_data).AsArray;
			return logBuyCoinData;
		}
		return logBuyCoinData;
	}

	public static void clearLogBuyCoinData() {
		PlayerPrefs.DeleteKey ("log_buy_coin_data");
		PlayerPrefs.Save ();
	}

	//log click ads
	public static bool isClickAdsID(int ads_id) {
		return PlayerPrefs.GetInt ("click_ads_"+ ads_id, 0) == 0 ? false : true;
	}

	public static void setClickAdsID(int ads_id, int clicked) {
		PlayerPrefs.SetInt ("click_ads_"+ ads_id, clicked);
		PlayerPrefs.Save ();
	}
}
