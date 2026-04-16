package org.pedrov.presentationtimer

import android.content.Context

class PhasesRepository(context: Context) {
    private val prefs = context.getSharedPreferences("phases_prefs", Context.MODE_PRIVATE)

    fun loadPhases(): List<PhaseConfig> {
        val json = prefs.getString("phases", null) ?: return PhaseConfig.defaults
        return try {
            PhaseConfig.listFromJson(json).sortedByDescending { it.thresholdPercent }
        } catch (e: Exception) {
            PhaseConfig.defaults
        }
    }

    fun savePhases(phases: List<PhaseConfig>) {
        prefs.edit().putString("phases", PhaseConfig.listToJson(phases)).apply()
    }
}
