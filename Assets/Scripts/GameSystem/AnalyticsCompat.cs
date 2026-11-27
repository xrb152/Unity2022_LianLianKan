using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// 轻量埋点占位实现。
/// 原工程用的是 Unity Analytics 包（com.unity.ads / com.unity.analytics 已移除），
/// 这里保留同名 API，调用点无需修改；后续要接抖音埋点，直接在此处转发给 TT 的统计接口即可。
/// </summary>
public static class Analytics
{
    public static void CustomEvent(string eventName, Dictionary<string, object> eventData)
    {
        if (string.IsNullOrEmpty(eventName))
            return;

        string payload = "";
        if (eventData != null)
        {
            foreach (KeyValuePair<string, object> kv in eventData)
                payload += kv.Key + "=" + kv.Value + " ";
        }
        Debug.Log("[Analytics] " + eventName + " " + payload);
    }

    public static void CustomEvent(string eventName)
    {
        CustomEvent(eventName, null);
    }
}
