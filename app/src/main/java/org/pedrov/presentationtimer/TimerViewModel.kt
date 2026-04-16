package org.pedrov.presentationtimer

import android.os.CountDownTimer
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

enum class TimerPhase { SETUP, RUNNING, PAUSED, FINISHED }

data class TimerState(
    val totalSeconds: Long = 0L,
    val remainingMillis: Long = 0L,
    val phase: TimerPhase = TimerPhase.SETUP,
    val activePhase: PhaseConfig? = null,
    val isFlashing: Boolean = false
)

class TimerViewModel : ViewModel() {

    private val _state = MutableLiveData(TimerState())
    val state: LiveData<TimerState> = _state

    var phases: List<PhaseConfig> = PhaseConfig.defaults
        set(value) {
            field = value.sortedByDescending { it.thresholdPercent }
            val current = _state.value ?: return
            if (current.phase == TimerPhase.RUNNING || current.phase == TimerPhase.PAUSED) {
                _state.value = current.copy(
                    activePhase = computePhase(current.remainingMillis, current.totalSeconds * 1000L)
                )
            }
        }

    private var countDownTimer: CountDownTimer? = null
    private var totalMillis: Long = 0L
    private var remainingMillis: Long = 0L

    fun setDuration(hours: Int, minutes: Int, seconds: Int) {
        totalMillis = ((hours * 3600L) + (minutes * 60L) + seconds) * 1000L
        remainingMillis = totalMillis
        _state.value = TimerState(
            totalSeconds = totalMillis / 1000L,
            remainingMillis = totalMillis,
            phase = TimerPhase.SETUP,
            activePhase = phases.maxByOrNull { it.thresholdPercent }
        )
    }

    fun start() {
        if (totalMillis <= 0L) return
        val currentPhase = _state.value?.phase ?: return
        if (currentPhase == TimerPhase.RUNNING) return
        launchTimer(remainingMillis)
    }

    fun pause() {
        countDownTimer?.cancel()
        _state.value = _state.value?.copy(phase = TimerPhase.PAUSED)
    }

    fun reset() {
        countDownTimer?.cancel()
        remainingMillis = totalMillis
        _state.value = TimerState(
            totalSeconds = totalMillis / 1000L,
            remainingMillis = totalMillis,
            phase = TimerPhase.SETUP,
            activePhase = phases.maxByOrNull { it.thresholdPercent }
        )
    }

    private fun launchTimer(fromMillis: Long) {
        countDownTimer?.cancel()
        countDownTimer = object : CountDownTimer(fromMillis, 100) {
            override fun onTick(millisUntilFinished: Long) {
                remainingMillis = millisUntilFinished
                _state.value = TimerState(
                    totalSeconds = totalMillis / 1000L,
                    remainingMillis = millisUntilFinished,
                    phase = TimerPhase.RUNNING,
                    activePhase = computePhase(millisUntilFinished, totalMillis)
                )
            }

            override fun onFinish() {
                remainingMillis = 0L
                _state.value = TimerState(
                    totalSeconds = totalMillis / 1000L,
                    remainingMillis = 0L,
                    phase = TimerPhase.FINISHED,
                    activePhase = phases.minByOrNull { it.thresholdPercent },
                    isFlashing = true
                )
            }
        }.start()

        _state.value = _state.value?.copy(phase = TimerPhase.RUNNING)
    }

    private fun computePhase(remainingMillis: Long, totalMillis: Long): PhaseConfig? {
        if (phases.isEmpty()) return null
        if (totalMillis == 0L) return phases.maxByOrNull { it.thresholdPercent }
        val percent = ((remainingMillis.toDouble() / totalMillis.toDouble()) * 100).toInt()
        val sorted = phases.sortedByDescending { it.thresholdPercent }
        return sorted.firstOrNull { percent >= it.thresholdPercent } ?: sorted.last()
    }

    override fun onCleared() {
        super.onCleared()
        countDownTimer?.cancel()
    }
}
