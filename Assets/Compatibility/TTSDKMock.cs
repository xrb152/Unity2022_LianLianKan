// TTSDK 占位层（未接入官方抖音小游戏 SDK 时使用）
//
// 背景：Assets/AdSDK/Scripts 下的广告脚本直接 using TTSDK，工程里没有官方 SDK 时
//       Assembly-CSharp 会整包编译失败（error CS0246），编辑器里所有脚本都会失效。
//
// 本文件只提供这些脚本用到的 TTSDK API 的最小实现，内部用日志模拟，让工程能编译、能跑。
// 以后真正导入官方 TTSDK（ByteGame / TTSDK 包）时，在
//       Project Settings → Player → Scripting Define Symbols 里加上 TTSDK_PRESENT
// 本文件就会整体跳过，不会和官方类型重复定义。

#if !TTSDK_PRESENT

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using TTSDK.UNBridgeLib.LitJson;
using UnityEngine;

namespace TTSDK.UNBridgeLib.LitJson
{
    public enum JsonType
    {
        None,
        Object,
        Array,
        String,
        Int,
        Long,
        Double,
        Boolean
    }

    /// <summary>
    /// LitJson.JsonData 的精简实现，只覆盖本项目用到的读写与序列化能力。
    /// </summary>
    public class JsonData
    {
        private JsonType type = JsonType.Object;
        private readonly Dictionary<string, JsonData> objectValues = new Dictionary<string, JsonData>();
        private readonly List<JsonData> arrayValues = new List<JsonData>();
        private string stringValue = string.Empty;
        private double numberValue;
        private bool boolValue;

        public JsonData()
        {
        }

        public JsonData(string value)
        {
            type = JsonType.String;
            stringValue = value ?? string.Empty;
        }

        public JsonData(int value)
        {
            type = JsonType.Int;
            numberValue = value;
        }

        public JsonData(long value)
        {
            type = JsonType.Long;
            numberValue = value;
        }

        public JsonData(double value)
        {
            type = JsonType.Double;
            numberValue = value;
        }

        public JsonData(bool value)
        {
            type = JsonType.Boolean;
            boolValue = value;
        }

        public JsonType GetJsonType()
        {
            return type;
        }

        public void SetJsonType(JsonType newType)
        {
            type = newType;
        }

        public JsonData this[string key]
        {
            get
            {
                JsonData value;
                if (!objectValues.TryGetValue(key, out value))
                {
                    value = new JsonData();
                    objectValues[key] = value;
                }

                return value;
            }
            set
            {
                type = JsonType.Object;
                objectValues[key] = value ?? new JsonData();
            }
        }

        public int Count
        {
            get { return type == JsonType.Array ? arrayValues.Count : objectValues.Count; }
        }

        public void Add(JsonData value)
        {
            if (type != JsonType.Array)
            {
                type = JsonType.Array;
            }

            arrayValues.Add(value ?? new JsonData());
        }

        public static implicit operator JsonData(string value)
        {
            return new JsonData(value);
        }

        public static implicit operator JsonData(int value)
        {
            return new JsonData(value);
        }

        public static implicit operator JsonData(long value)
        {
            return new JsonData(value);
        }

        public static implicit operator JsonData(double value)
        {
            return new JsonData(value);
        }

        public static implicit operator JsonData(bool value)
        {
            return new JsonData(value);
        }

        public override string ToString()
        {
            return ToJson();
        }

        public string ToJson()
        {
            var builder = new StringBuilder();
            Write(builder, this);
            return builder.ToString();
        }

        private static void Write(StringBuilder builder, JsonData data)
        {
            if (data == null)
            {
                builder.Append("null");
                return;
            }

            switch (data.type)
            {
                case JsonType.Object:
                    builder.Append('{');
                    var first = true;
                    foreach (var pair in data.objectValues)
                    {
                        if (!first)
                        {
                            builder.Append(',');
                        }

                        first = false;
                        builder.Append('"').Append(Escape(pair.Key)).Append("\":");
                        Write(builder, pair.Value);
                    }

                    builder.Append('}');
                    break;

                case JsonType.Array:
                    builder.Append('[');
                    for (var i = 0; i < data.arrayValues.Count; i++)
                    {
                        if (i > 0)
                        {
                            builder.Append(',');
                        }

                        Write(builder, data.arrayValues[i]);
                    }

                    builder.Append(']');
                    break;

                case JsonType.String:
                    builder.Append('"').Append(Escape(data.stringValue)).Append('"');
                    break;

                case JsonType.Boolean:
                    builder.Append(data.boolValue ? "true" : "false");
                    break;

                case JsonType.None:
                    builder.Append("null");
                    break;

                default:
                    builder.Append(data.numberValue.ToString(CultureInfo.InvariantCulture));
                    break;
            }
        }

        private static string Escape(string value)
        {
            if (string.IsNullOrEmpty(value))
            {
                return string.Empty;
            }

            return value
                .Replace("\\", "\\\\")
                .Replace("\"", "\\\"")
                .Replace("\n", "\\n")
                .Replace("\r", "\\r")
                .Replace("\t", "\\t");
        }
    }
}

namespace TTSDK
{
    /// <summary>系统信息（占位数据）。</summary>
    public class TTSystemInfo
    {
        public string system = "editor";
        public string platform = "editor";
        public string brand = "Unity";
        public string model = "UnityEditor";
        public string ttVersion = "0.0.0";
        public string sdkVersion = "mock";
        public string hostName = "UnityEditor";
        public int screenWidth;
        public int screenHeight;

        public override string ToString()
        {
            return string.Format("system={0}, platform={1}, brand={2}, model={3}", system, platform, brand, model);
        }
    }

    /// <summary>用户信息（占位数据）。</summary>
    public class TTUserInfo
    {
        public string nickName = "EditorUser";
        public string avatarUrl = string.Empty;
        public string openId = "mock_openid";
        public string gender = string.Empty;
        public string city = string.Empty;
        public string province = string.Empty;
        public string country = string.Empty;
        public string language = string.Empty;

        public override string ToString()
        {
            return string.Format("openId={0}, nickName={1}", openId, nickName);
        }
    }

    /// <summary>启动参数（占位数据）。</summary>
    public class TTLaunchOptions
    {
        public string Scene = string.Empty;
        public Dictionary<string, string> Query = new Dictionary<string, string>();
    }

    public class ContainerEnv
    {
    }

    public class CreateRewardedVideoAdParam
    {
        public string AdUnitId;
    }

    public class CreateInterstitialAdParam
    {
        public string InterstitialAdId;
    }

    /// <summary>获取用户信息的回调：官方 SDK 使用 ref 参数，这里保持一致。</summary>
    public delegate void TTGetUserInfoCallback(ref TTUserInfo userInfo);

    /// <summary>激励视频广告（占位实现）。</summary>
    public class TTRewardedVideoAd
    {
        public event Action<bool, int> OnClose;
        public event Action<int, string> OnError;
        public event Action OnLoad;

        private bool destroyed;

        public void Load()
        {
            if (destroyed)
            {
                return;
            }

            TT.LogMock("TTRewardedVideoAd.Load()");
            if (OnLoad != null)
            {
                OnLoad();
            }
        }

        public void Show()
        {
            if (destroyed)
            {
                RaiseError("广告实例已销毁");
                return;
            }

            TT.LogMock("TTRewardedVideoAd.Show()");

            // 编辑器里默认模拟"看完广告"，方便调试发奖流程；
            // 想看失败分支时把 TT.MockAdSuccess 设为 false。
            if (TT.MockAdSuccess)
            {
                if (OnClose != null)
                {
                    OnClose(true, 1);
                }
            }
            else
            {
                RaiseError("编辑器占位层：没有接入真实广告 SDK");
            }
        }

        public void Destroy()
        {
            destroyed = true;
            OnClose = null;
            OnError = null;
            OnLoad = null;
        }

        private void RaiseError(string message)
        {
            if (OnError != null)
            {
                OnError(-1, message);
            }
        }
    }

    /// <summary>插屏广告（占位实现）。</summary>
    public class TTInterstitialAd
    {
        public event Action OnClose;
        public event Action OnLoad;
        public event Action<int, string> OnError;

        private bool destroyed;

        public bool IsLoaded()
        {
            return !destroyed;
        }

        public void Load()
        {
            if (destroyed)
            {
                return;
            }

            TT.LogMock("TTInterstitialAd.Load()");
            if (OnLoad != null)
            {
                OnLoad();
            }
        }

        public void Show()
        {
            if (destroyed)
            {
                RaiseError("广告实例已销毁");
                return;
            }

            TT.LogMock("TTInterstitialAd.Show()");
            if (OnClose != null)
            {
                OnClose();
            }
        }

        public void Destroy()
        {
            destroyed = true;
            OnClose = null;
            OnLoad = null;
            OnError = null;
        }

        private void RaiseError(string message)
        {
            if (OnError != null)
            {
                OnError(-1, message);
            }
        }
    }

    /// <summary>
    /// 抖音小游戏 SDK 入口占位实现：所有接口都不会抛异常，只在控制台打日志。
    /// </summary>
    public static class TT
    {
        /// <summary>占位层模拟广告是否"看完"，默认成功，便于在编辑器里调试发奖流程。</summary>
        public static bool MockAdSuccess = true;

        private const string Tag = "[TTSDK占位层]";

        public static void LogMock(string api)
        {
            Debug.Log(Tag + " " + api);
        }

        public static void InitSDK(Action<int, ContainerEnv> onInit)
        {
            LogMock("InitSDK()");
            if (onInit != null)
            {
                onInit(0, new ContainerEnv());
            }
        }

        public static TTSystemInfo GetSystemInfo()
        {
            return new TTSystemInfo
            {
                screenWidth = Screen.width,
                screenHeight = Screen.height
            };
        }

        public static TTLaunchOptions GetLaunchOptionsSync()
        {
            return new TTLaunchOptions();
        }

        public static TTRewardedVideoAd CreateRewardedVideoAd(CreateRewardedVideoAdParam param)
        {
            LogMock("CreateRewardedVideoAd(" + (param == null ? "null" : param.AdUnitId) + ")");
            return new TTRewardedVideoAd();
        }

        public static TTInterstitialAd CreateInterstitialAd(CreateInterstitialAdParam param)
        {
            LogMock("CreateInterstitialAd(" + (param == null ? "null" : param.InterstitialAdId) + ")");
            return new TTInterstitialAd();
        }

        public static void NavigateToScene(JsonData data, Action onSuccess, Action onComplete, Action<int, string> onError)
        {
            LogMock("NavigateToScene(" + data + ")");
            if (onSuccess != null)
            {
                onSuccess();
            }

            if (onComplete != null)
            {
                onComplete();
            }
        }

        public static void Login(Action<string, string, bool> onSuccess, Action<string> onFail, bool force = false)
        {
            LogMock("Login(force=" + force + ")");
            if (onSuccess != null)
            {
                onSuccess("mock_code", "mock_anonymous_code", true);
            }
        }

        public static void GetUserInfo(TTGetUserInfoCallback onSuccess, Action<string> onFail)
        {
            LogMock("GetUserInfo()");
            var userInfo = new TTUserInfo();
            if (onSuccess != null)
            {
                onSuccess(ref userInfo);
            }
        }

        public static void CheckSession(Action onSuccess, Action<string> onFail)
        {
            LogMock("CheckSession()");
            if (onSuccess != null)
            {
                onSuccess();
            }
        }

        public static void ShareAppMessage(JsonData data, Action<JsonData> onSuccess = null, Action<string> onFail = null, Action onCancel = null)
        {
            LogMock("ShareAppMessage(" + data + ")");
            if (onSuccess != null)
            {
                onSuccess(data);
            }
        }

        public static void SetImRankData(JsonData data, Action<bool, string> onComplete)
        {
            LogMock("SetImRankData(" + data + ")");
            if (onComplete != null)
            {
                onComplete(true, "mock: 排行榜数据已模拟上传");
            }
        }

        public static void GetImRankList(JsonData data, Action<bool, string> onComplete)
        {
            LogMock("GetImRankList(" + data + ")");
            if (onComplete != null)
            {
                onComplete(true, "mock: 排行榜数据为空");
            }
        }
    }
}

#endif
