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
            PhaseConfig(name = "On track",    thresholdPercent = 50, colorHex = "#2E7D32", message = "On track \uD83D\uDFE2"),
            PhaseConfig(name = "Hurry up",    thresholdPercent = 20, colorHex = "#F9A825", message = "Hurry up! \uD83D\uDFE1"),
            PhaseConfig(name = "Almost done", thresholdPercent = 0,  colorHex = "#C62828", message = "Almost out of time! \uD83D\uDD34")
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
