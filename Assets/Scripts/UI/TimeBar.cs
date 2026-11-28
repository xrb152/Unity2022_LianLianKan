using UnityEngine;
using System.Collections;
using UnityEngine.UI;
using System.Collections.Generic;


public class TimeBar : MonoBehaviour {
	float totalTime = 100;
	float currentTime = 0;
	bool isRun = false;
	public ResultBar levelFail;
	public Image fillImage;
	public RectTransform start;
	public RectTransform end;
	float timeStar1;
	float timeStar2;
	float timeStar3;
	int numStar = 3;
	bool _isTrigger1MinSound = false;

	[Header("用数字倒计时取代绿条和三颗星")]
	[Tooltip("关掉就恢复原来的绿色进度条 + 三颗星。绿条只显示剩余比例、星星是三星时间线，玩家容易误以为是消除进度。")]
	public bool useCountdownText = true;

	[Header("倒计时最后多少秒变红")]
	public int warnSeconds = 30;

	Text countdownText;
	int shownSecond = -1;

	void Start () {
		if (useCountdownText)
			setupCountdownUI ();
	}

	// Update is called once per frame
	void Update () {
		if (isRun) {
            currentTime -= Time.smoothDeltaTime;
			if (!_isTrigger1MinSound && currentTime < 60) {
				_isTrigger1MinSound = true;
				SoundSystem.ins.play_time_over_in_1_min ();
			}
			fillImage.fillAmount = currentTime/totalTime;
			if(currentTime <= 0){
				isRun =false;
				timeOut();
			}
			// numStar 决定结算星级，无论界面上有没有星星都要照常递减
			if(totalTime - currentTime > timeStar1 && numStar == 3){
				numStar = 2;
				if (!useCountdownText) transform.Find("Star1").gameObject.SetActive(false);
			}
			if(totalTime - currentTime > timeStar2 && numStar == 2){
				numStar = 1;
				if (!useCountdownText) transform.Find("Star2").gameObject.SetActive(false);
			}
			if(totalTime - currentTime > timeStar3 && numStar == 1){
				numStar = 0;
				if (!useCountdownText) transform.Find("Star3").gameObject.SetActive(false);
			}
			refreshCountdown ();
		}
	}

	public void startBar(float time){
		totalTime = time;
		currentTime = totalTime;
		isRun = true;
		numStar = 3;
		_isTrigger1MinSound = false;
		shownSecond = -1;
		refreshCountdown ();
	}

	public void startBar(float totalTime, float currentTime) {
//		totalTime = 110;
//		currentTime = 5;
		this.totalTime = totalTime;
		this.currentTime = currentTime;
		isRun = true;
		numStar = 3;
		_isTrigger1MinSound = false;
		shownSecond = -1;
		refreshCountdown ();
	}

	public void setTarget(float timeStar1, float timeStar2, float timeStar3){
		this.timeStar1 = timeStar1;
		this.timeStar2 = timeStar2;
		this.timeStar3 = timeStar3;
		if (useCountdownText)
			return;	// 星星已经隐藏，不用再摆位置
		float dis = start.anchoredPosition.x - end.anchoredPosition.x;
		transform.Find("Star1").gameObject.SetActive(true);
		transform.Find("Star2").gameObject.SetActive(true);
		transform.Find("Star3").gameObject.SetActive(true);
		transform.Find ("Star1").GetComponent<RectTransform> ().anchoredPosition = new Vector2 (start.anchoredPosition.x - timeStar1 * dis / totalTime, start.anchoredPosition.y);
		transform.Find ("Star2").GetComponent<RectTransform> ().anchoredPosition = new Vector2 (start.anchoredPosition.x - timeStar2 * dis / totalTime, start.anchoredPosition.y);
		transform.Find ("Star3").GetComponent<RectTransform> ().anchoredPosition = new Vector2 (start.anchoredPosition.x - timeStar3 * dis / totalTime, start.anchoredPosition.y);
	}

	public void pause(){
		isRun = false;
	}

	public void continueRun(){
		isRun = true;
	}
	public int getNumStar(){
		return numStar;
	}

	public int getTimeRun(){
		return (int) (totalTime - currentTime);
	}

	public int getTimeRemain() {
		return (int) currentTime;
	}

	// ---------------- 数字倒计时 ----------------

	/// <summary>
	/// 隐藏白底条、绿色进度条和三颗星，在原来的位置上放一个居中的 mm:ss。
	/// 全部运行时构建、不改场景：Unity 编辑器不重读磁盘上的场景文件，
	/// 改 YAML 还得让玩家重开场景才看得到。
	/// </summary>
	void setupCountdownUI() {
		Image bg = GetComponent<Image> ();
		if (bg != null)
			bg.enabled = false;		// 白色底条

		hideChild ("FillBar");		// 绿色进度条
		hideChild ("Star1");
		hideChild ("Star2");
		hideChild ("Star3");

		GameObject go = new GameObject ("Countdown", typeof(RectTransform));
		go.layer = gameObject.layer;
		go.transform.SetParent (transform, false);

		RectTransform rt = (RectTransform)go.transform;
		rt.anchorMin = Vector2.zero;
		rt.anchorMax = Vector2.one;
		rt.offsetMin = Vector2.zero;
		rt.offsetMax = Vector2.zero;

		countdownText = go.AddComponent<Text> ();
		countdownText.font = findUIFont ();
		countdownText.fontSize = 24;
		countdownText.fontStyle = FontStyle.Bold;
		countdownText.alignment = TextAnchor.MiddleCenter;
		countdownText.horizontalOverflow = HorizontalWrapMode.Overflow;
		countdownText.verticalOverflow = VerticalWrapMode.Overflow;
		countdownText.raycastTarget = false;
		countdownText.color = Color.white;

		Outline outline = go.AddComponent<Outline> ();
		outline.effectColor = new Color (0f, 0f, 0f, 0.55f);
		outline.effectDistance = new Vector2 (1.2f, -1.2f);

		refreshCountdown ();
	}

	void hideChild(string childName) {
		Transform t = transform.Find (childName);
		if (t != null)
			t.gameObject.SetActive (false);
	}

	/// <summary>只在秒数变化时写文本，避免每帧触发 UI 重建。</summary>
	void refreshCountdown() {
		if (countdownText == null)
			return;
		int sec = Mathf.Max (0, Mathf.CeilToInt (currentTime));
		if (sec == shownSecond)
			return;
		shownSecond = sec;
		countdownText.text = (sec / 60).ToString ("00") + ":" + (sec % 60).ToString ("00");
		countdownText.color = sec <= warnSeconds
			? new Color (1f, 0.30f, 0.30f)
			: Color.white;
	}

	/// <summary>沿用场景里已有的中文字体，和分数、关卡数字一致。</summary>
	static Font findUIFont() {
		Font[] fonts = Resources.FindObjectsOfTypeAll<Font> ();
		if (fonts != null) {
			for (int i = 0; i < fonts.Length; i++) {
				if (fonts [i] != null && fonts [i].name.IndexOf ("Droid", System.StringComparison.OrdinalIgnoreCase) >= 0)
					return fonts [i];
			}
		}
		Font f = Resources.Load<Font> ("Font/CarterOne");
		if (f != null)
			return f;
		return Resources.GetBuiltinResource<Font> ("LegacyRuntime.ttf");
	}

	void timeOut(){
		numStar = 0;
		GameStatic.map.gameOver (true);
	}
}
