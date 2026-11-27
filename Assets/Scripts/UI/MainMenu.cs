using UnityEngine;
using System.Collections;
using UnityEngine.SceneManagement;
using UnityEngine.UI;


public class MainMenu : MonoBehaviour {
	// public Button btnContinue;
	public GameObject btnContinue;
	// public GameObject btnDebugPostScore;
	// public GameObject btnDebugResetHighScore;
	public GameObject chooseModePopup;
	//public GameObject btnEvent;
	//public TimeCountDown timeEventRamain;

	// public BannerView bannerViewLeft;
	// public BannerView bannerViewRight;

	bool isShowChooseModeDialog = false;
	float currentTime;
//	float timeReloadRequestBanner = 10;
//	string admob_id_2003 = "ca-app-pub-3940256099942544/6300978111";
//	string admob_id_2017 = "ca-app-pub-3940256099942544/6300978111";
	void Start(){
//		Save.setTutorial(0);
		// Save.setTutorialStore(0);
		btnContinue.SetActive(Save.canContinue());
		// btnDebugPostScore.SetActive (GameConfig.DEBUG_KEY);
		// btnDebugResetHighScore.SetActive (GameConfig.DEBUG_KEY);
		// updateButtonEventUI ();
	}
	void Update() {
		if (Save.getTutorialStatus() == 0) {
			Tutorial.TUTORIAL_MODE = 0;
			SceneManager.LoadScene ("Help");
			//AdsManager.ins.hideBannerView ();

		}
	}
	public void StartOfflineMode(){
		SceneManager.LoadScene ("LevelSence");
	}
	public void StartOnlineMode(){
		SceneManager.LoadScene ("OnlinePlay");
	}
	public void StartTutorial() {
		Tutorial.TUTORIAL_MODE = 0;
		SceneManager.LoadScene ("Help");
	}

    public void QuitGame()
    {
#if !UNITY_IOS
        if (Save.getRateStatus() == Const.STATUS_RATE_REMIND && Save.canShowRate())
        {
            GameStatic.ratePopup.showPopup();
        }
        else
        {
            GameStatic.handleQuitApp();
        }
#endif
    }

    //public void showLeaderBoard() {
    //	if (GameStatic.IsConnectedGooglePlayService) {
    //		CustomDebug.Log ("show LeaderBoard");
    //		Social.ShowLeaderboardUI ();
    //	} else {
    //		ToastManager.showToast ("Unable connect to google play service, will connect again");
    //		GameStatic.ConnectToGooglePlayService ();
    //	}
    //}

    public void showChooseModePopup() {
		chooseModePopup.transform.parent.gameObject.SetActive(true);
        chooseModePopup.GetComponent<Animator>().Play("showpause");
    }

	public void hideChoo2seModePopup() {
        Invoke("hideParent", 0.2f);
        chooseModePopup.GetComponent<Animator>().Play("hidepause");
	}

    void hideParent()
    {
        chooseModePopup.transform.parent.gameObject.SetActive(false);
    }

    //public void hideBannerView() {
    //    AdsManager.ins.hideBannerView();
    //}

	public void endAnimaMain() {
		//AdsManager.ins.showBannerView();
		updateButtonEventUI();
		//GameStatic.networkConnectionStatus.checkNetwork (result => {
		//	if (result) {
		//		int rand = UnityEngine.Random.Range(0, 100);
		//		if (rand < GameConfig.probability_ads_visible) {
		//			GameStatic.adsPopup.loadAds ();	
		//		}
		//	}	
		//});
	}

	public void updateButtonEventUI() {
		//bool hasEvent = GSM.instance.eventData == null ? false : true;
		//btnEvent.SetActive (hasEvent);
		//if (hasEvent) {
		//	int status = (int) GSM.instance.eventData.GetInt("status");
		//	string eventName = (string) GSM.instance.eventData.GetString("event_name");
		//	if (status == EventInfo.STATUS_PREPARE) {
		//		timeEventRamain.setText("Preparing Time");
		//	} else if (status == EventInfo.STATUS_ONGOING) {
		//		timeEventRamain.StartRun ((int)(GSM.instance.eventData.GetLong ("time") / 1000),done=>{
		//			GSM.instance.getEventData();
		//		});
		//	} else {
		//		timeEventRamain.setText("Event ended");
		//	}
		//}
		// btnContinueEvent.SetActive (hasEvent && Save.canContinueEvent ());
	}

	public void showEventMainUI() {
		//GameStatic.eventArea.show ();
	}

    public void showMoreApp()
    {

    }
}
