package org.pedrov.presentationtimer

import org.json.JSONArray
import org.json.JSONObject
import java.util.UUID

data class PhaseConfig(
    val id: String = UUID.randomUUID().toString(),
    val name: String,
    val thresholdPercent: Int,
    val colorHex: String,
    val message: String
) {
    fun toJson(): JSONObject = JSONObject().apply {
        put("id", id)
        put("name", name)
        put("thresholdPercent", thresholdPercent)
        put("colorHex", colorHex)
        put("message", message)
    }

    companion object {
        fun fromJson(obj: JSONObject) = PhaseConfig(
            id = obj.getString("id"),
            name = obj.getString("name"),
            thresholdPercent = obj.getInt("thresholdPercent"),
            colorHex = obj.getString("colorHex"),
            message = obj.getString("message")
        )

        val defaults = listOf(
            PhaseConfig(name = "On track",    thresholdPercent = 50, colorHex = "#5AF0B3", message = "On track"),
            PhaseConfig(name = "Hurry up",    thresholdPercent = 20, colorHex = "#FFB95F", message = "Hurry up!"),
            PhaseConfig(name = "Almost done", thresholdPercent = 0,  colorHex = "#FFCAC5", message = "Almost out of time!")
        )

        fun listToJson(phases: List<PhaseConfig>): String {
            val arr = JSONArray()
            phases.forEach { arr.put(it.toJson()) }
            return arr.toString()
        }

        fun listFromJson(json: String): List<PhaseConfig> {
            val arr = JSONArray(json)
            return (0 until arr.length()).map { fromJson(arr.getJSONObject(it)) }
        }
    }
}
