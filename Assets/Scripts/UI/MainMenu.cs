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
	// 可选的"更多游戏"按钮：原用于应用商店引流，链接已移除（showMoreApp 空实现），
	// 按钮点了没反应会被判"虚假按钮"，Start 里统一隐藏。Inspector 没绑定时按名字兜底查找。
	public GameObject btnMore;
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
		hideInactiveButtons();
		// btnDebugPostScore.SetActive (GameConfig.DEBUG_KEY);
		// btnDebugResetHighScore.SetActive (GameConfig.DEBUG_KEY);
		// updateButtonEventUI ();
	}

	// 隐藏没有实际功能的按钮（抖音审核：界面上不能有点了没反应的按钮），并把剩余按钮整体居中
	void hideInactiveButtons(){
		GameObject more = btnMore != null ? btnMore : GameObject.Find("btnMore");
		if (more == null) return;
		Transform group = more.transform.parent;
		more.SetActive(false);
		recenterButtons(group);
	}

	// buttonGroup 里三个按钮是等距硬定位的，去掉一个后要重排，否则剩下的会偏一侧
	void recenterButtons(Transform group){
		if (group == null) return;
		var items = new System.Collections.Generic.List<RectTransform>();
		foreach (Transform child in group) {
			RectTransform rt = child as RectTransform;
			if (rt != null && rt.gameObject.activeSelf) items.Add(rt);
		}
		if (items.Count < 2) return;	// 只剩一个时不处理，它本来就在中心
		items.Sort((a, b) => a.anchoredPosition.x.CompareTo(b.anchoredPosition.x));
		// 用现有最小相邻间距作为统一间距
		float gap = float.MaxValue;
		for (int i = 1; i < items.Count; i++) {
			float d = items[i].anchoredPosition.x - items[i - 1].anchoredPosition.x;
			if (d > 0.01f && d < gap) gap = d;
		}
		if (gap == float.MaxValue) return;
		float start = -gap * (items.Count - 1) * 0.5f;
		for (int i = 0; i < items.Count; i++) {
			Vector2 p = items[i].anchoredPosition;
			items[i].anchoredPosition = new Vector2(start + gap * i, p.y);
		}
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

    // 原"更多游戏"入口，跳应用商店的代码已被移除，现为空实现。
    // 按钮在 hideInactiveButtons() 里隐藏；此方法保留仅为避免场景里 Button.onClick 引用变成 Missing。
    public void showMoreApp()
    {

    }
}
