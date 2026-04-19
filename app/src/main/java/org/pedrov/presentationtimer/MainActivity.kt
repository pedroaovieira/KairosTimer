package org.pedrov.presentationtimer

import android.animation.ValueAnimator
import android.content.Intent
import android.content.res.ColorStateList
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import androidx.core.graphics.ColorUtils
import android.os.Bundle
import android.view.View
import android.view.WindowManager
import android.view.animation.AccelerateDecelerateInterpolator
import android.view.animation.AlphaAnimation
import android.view.animation.Animation
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import org.pedrov.presentationtimer.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val viewModel: TimerViewModel by viewModels()
    private lateinit var repository: PhasesRepository

    private var flashAnimation: AlphaAnimation? = null
    private var auraColorAnimator: ValueAnimator? = null
    private var bgAnimator: ValueAnimator? = null
    private var haloAnimator: ValueAnimator? = null

    private var currentAuraColor: Int = Color.parseColor("#5AF0B3")
    private var currentBgColor: Int = Color.parseColor("#1A1A1A")

    private val darkInk = Color.parseColor("#0D0D0D")
    private val darkBg  = Color.parseColor("#1A1A1A")

    private val settingsLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) {
        viewModel.phases = repository.loadPhases()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        repository = PhasesRepository(this)
        viewModel.phases = repository.loadPhases()

        setupClickListeners()
        observeViewModel()
    }

    private fun setupClickListeners() {
        // INITIALIZE
        binding.btnStart.setOnClickListener {
            val phase = viewModel.state.value?.phase
            if (phase == TimerPhase.SETUP) {
                val h = binding.inputHours.text.toString().toIntOrNull() ?: 0
                val m = binding.inputMinutes.text.toString().toIntOrNull() ?: 0
                val s = binding.inputSeconds.text.toString().toIntOrNull() ?: 0
                viewModel.setDuration(h, m, s)
                viewModel.start()
            }
        }

        // Segmented: PAUSE (running) / RESUME (paused)
        binding.btnPauseSegment.setOnClickListener {
            when (viewModel.state.value?.phase) {
                TimerPhase.RUNNING -> viewModel.pause()
                TimerPhase.PAUSED  -> viewModel.start()
                else               -> {}
            }
        }

        // Segmented: STOP (running or paused)
        binding.btnResetSegment.setOnClickListener {
            stopFlashAnimation()
            stopHaloAnimation()
            viewModel.reset()
        }

        // Standalone RESET (finished)
        binding.btnReset.setOnClickListener {
            stopFlashAnimation()
            stopHaloAnimation()
            viewModel.reset()
        }

        binding.btnSettings.setOnClickListener {
            settingsLauncher.launch(Intent(this, SettingsActivity::class.java))
        }

        // Pace presets
        val presets = listOf(
            binding.btnPreset5  to Pair(0, 5),
            binding.btnPreset15 to Pair(0, 15),
            binding.btnPreset25 to Pair(0, 25),
            binding.btnPreset45 to Pair(0, 45),
        )
        presets.forEach { (btn, hm) ->
            btn.setOnClickListener {
                binding.inputHours.setText("")
                binding.inputMinutes.setText(hm.second.toString())
                binding.inputSeconds.setText("")
            }
        }
    }

    private fun observeViewModel() {
        viewModel.state.observe(this) { state ->
            updateTimerDisplay(state)
            updateAccentColor(state)
            updateButtons(state)
        }
    }

    private fun updateTimerDisplay(state: TimerState) {
        val totalSecs = state.remainingMillis / 1000L
        val hours   = totalSecs / 3600
        val minutes = (totalSecs % 3600) / 60
        val seconds = totalSecs % 60

        binding.tvTimer.text = if (hours > 0) {
            String.format("%d:%02d:%02d", hours, minutes, seconds)
        } else {
            String.format("%02d:%02d", minutes, seconds)
        }

        val progress = if (state.totalSeconds > 0) {
            ((state.remainingMillis.toFloat() / (state.totalSeconds * 1000f)) * 100).toInt()
        } else 100

        binding.progressArc.progress = progress
        binding.tvProgressPct.text = "$progress%"
    }

    private fun updateAccentColor(state: TimerState) {
        val colorHex   = state.activePhase?.colorHex ?: "#5AF0B3"
        val phaseColor = Color.parseColor(colorHex)
        val isActive   = state.phase != TimerPhase.SETUP

        // Root background
        val targetBg = if (isActive) phaseColor else darkBg
        if (targetBg != currentBgColor) {
            bgAnimator?.cancel()
            bgAnimator = ValueAnimator.ofArgb(currentBgColor, targetBg).apply {
                duration = 500
                addUpdateListener { anim -> binding.root.setBackgroundColor(anim.animatedValue as Int) }
                start()
            }
            currentBgColor = targetBg
        }

        // Aura bar + progress: phase colour on dark bg; dark ink on phase bg
        val targetAccent = if (isActive) darkInk else phaseColor
        if (targetAccent != currentAuraColor) {
            auraColorAnimator?.cancel()
            auraColorAnimator = ValueAnimator.ofArgb(currentAuraColor, targetAccent).apply {
                duration = 500
                addUpdateListener { anim ->
                    val c = anim.animatedValue as Int
                    binding.auraBar.setBackgroundColor(c)
                    binding.progressArc.setIndicatorColor(c)
                }
                start()
            }
            currentAuraColor = targetAccent
        }

        // Halo: blend phase colour 60% toward white so it's visible against the phase background
        val haloColor = ColorUtils.blendARGB(phaseColor, Color.WHITE, 0.6f)
        (binding.haloView.background as? GradientDrawable)?.setColor(haloColor)

        // Text colours
        val textColor    = if (isActive) darkInk else Color.parseColor("#E5E2E1")
        val labelColor   = if (isActive) darkInk else phaseColor
        binding.tvTimer.setTextColor(textColor)
        binding.tvPhaseLabel.setTextColor(labelColor)
        binding.tvAppName.setTextColor(if (isActive) darkInk else phaseColor)
        binding.tvProgressPct.setTextColor(if (isActive) darkInk else textColor)

        // Segmented button tints on phase background
        val pauseBg   = if (isActive) darkInk else phaseColor
        val pauseFg   = if (isActive) phaseColor else Color.parseColor("#003825")
        val stopBg    = if (isActive) Color.parseColor("#1A1A1A") else Color.parseColor("#353534")
        val stopFg    = if (isActive) phaseColor else Color.parseColor("#E5E2E1")

        binding.btnPauseSegment.backgroundTintList = ColorStateList.valueOf(pauseBg)
        binding.btnPauseSegment.setTextColor(pauseFg)
        binding.btnPauseSegment.iconTint = ColorStateList.valueOf(pauseFg)

        binding.btnResetSegment.backgroundTintList = ColorStateList.valueOf(stopBg)
        binding.btnResetSegment.setTextColor(stopFg)
        binding.btnResetSegment.iconTint = ColorStateList.valueOf(stopFg)

        // INITIALIZE button (setup only — always on dark bg)
        if (!isActive) {
            binding.btnStart.backgroundTintList = ColorStateList.valueOf(phaseColor)
            binding.btnStart.setTextColor(Color.parseColor("#003825"))
        }

        // RESET button (finished — on phase bg)
        binding.btnReset.backgroundTintList = ColorStateList.valueOf(stopBg)
        binding.btnReset.setTextColor(stopFg)

        // Flash / halo
        if (state.isFlashing) startFlashAnimation() else stopFlashAnimation()

        if (state.phase == TimerPhase.RUNNING) startHaloAnimation()
        else stopHaloAnimation()

        // Paused: fade digits to 55%
        binding.tvTimer.alpha = if (state.phase == TimerPhase.PAUSED) 0.55f else 1f

        binding.tvPhaseLabel.text = when (state.phase) {
            TimerPhase.SETUP    -> "READY"
            TimerPhase.RUNNING  -> (state.activePhase?.message ?: "ON TRACK").uppercase()
            TimerPhase.PAUSED   -> "PAUSED"
            TimerPhase.FINISHED -> "TIME'S UP"
        }
    }

    private fun updateButtons(state: TimerState) {
        binding.btnSettings.visibility = if (state.phase == TimerPhase.SETUP) View.VISIBLE else View.GONE

        val timerVisible = if (state.phase == TimerPhase.SETUP) View.GONE else View.VISIBLE
        binding.tvPhaseLabel.visibility = timerVisible
        binding.tvTimer.visibility      = timerVisible
        binding.progressRow.visibility  = timerVisible

        when (state.phase) {
            TimerPhase.SETUP -> {
                binding.setupPanel.visibility      = View.VISIBLE
                binding.segmentedControl.visibility = View.GONE
                binding.btnStart.visibility         = View.VISIBLE
                binding.btnStart.text               = "INITIALIZE"
                binding.btnReset.visibility         = View.GONE
            }
            TimerPhase.RUNNING -> {
                binding.setupPanel.visibility      = View.GONE
                binding.segmentedControl.visibility = View.VISIBLE
                binding.btnPauseSegment.text        = "PAUSE"
                binding.btnStart.visibility         = View.GONE
                binding.btnReset.visibility         = View.GONE
            }
            TimerPhase.PAUSED -> {
                binding.setupPanel.visibility      = View.GONE
                binding.segmentedControl.visibility = View.VISIBLE
                binding.btnPauseSegment.text        = "▶  RESUME"
                binding.btnStart.visibility         = View.GONE
                binding.btnReset.visibility         = View.GONE
            }
            TimerPhase.FINISHED -> {
                binding.setupPanel.visibility      = View.GONE
                binding.segmentedControl.visibility = View.GONE
                binding.btnStart.visibility         = View.GONE
                binding.btnReset.visibility         = View.VISIBLE
            }
        }
    }

    // ── Breathing halo ────────────────────────────────────────────────────────

    private fun startHaloAnimation() {
        binding.haloView.visibility = View.VISIBLE
        if (haloAnimator != null) return
        haloAnimator = ValueAnimator.ofFloat(0.82f, 1.08f).apply {
            duration = 2200
            repeatMode = ValueAnimator.REVERSE
            repeatCount = ValueAnimator.INFINITE
            interpolator = AccelerateDecelerateInterpolator()
            addUpdateListener { anim ->
                val s = anim.animatedValue as Float
                binding.haloView.scaleX = s
                binding.haloView.scaleY = s
                // alpha breathes between 0.10 and 0.30
                binding.haloView.alpha = 0.10f + ((s - 0.82f) / (1.08f - 0.82f)) * 0.20f
            }
            start()
        }
    }

    private fun stopHaloAnimation() {
        haloAnimator?.cancel()
        haloAnimator = null
        binding.haloView.visibility = View.GONE
        binding.haloView.alpha = 0f
    }

    // ── Flash animation ───────────────────────────────────────────────────────

    private fun startFlashAnimation() {
        if (flashAnimation != null) return
        flashAnimation = AlphaAnimation(1f, 0.15f).apply {
            duration = 600
            repeatMode = Animation.REVERSE
            repeatCount = Animation.INFINITE
        }
        binding.tvTimer.startAnimation(flashAnimation)
    }

    private fun stopFlashAnimation() {
        flashAnimation?.let {
            binding.tvTimer.clearAnimation()
            flashAnimation = null
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        stopFlashAnimation()
        stopHaloAnimation()
        auraColorAnimator?.cancel()
        bgAnimator?.cancel()
    }
}
