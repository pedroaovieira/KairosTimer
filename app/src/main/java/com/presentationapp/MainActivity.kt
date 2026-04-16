package com.presentationapp

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.view.WindowManager
import android.view.animation.AlphaAnimation
import android.view.animation.Animation
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.presentationapp.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val viewModel: TimerViewModel by viewModels()
    private lateinit var repository: PhasesRepository
    private var flashAnimation: AlphaAnimation? = null

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
        binding.btnStart.setOnClickListener {
            val phase = viewModel.state.value?.phase
            if (phase == TimerPhase.SETUP || phase == TimerPhase.PAUSED) {
                if (phase == TimerPhase.SETUP) {
                    val h = binding.inputHours.text.toString().toIntOrNull() ?: 0
                    val m = binding.inputMinutes.text.toString().toIntOrNull() ?: 0
                    val s = binding.inputSeconds.text.toString().toIntOrNull() ?: 0
                    viewModel.setDuration(h, m, s)
                }
                viewModel.start()
            }
        }

        binding.btnPause.setOnClickListener { viewModel.pause() }

        binding.btnReset.setOnClickListener {
            stopFlashAnimation()
            viewModel.reset()
        }

        binding.btnSettings.setOnClickListener {
            settingsLauncher.launch(Intent(this, SettingsActivity::class.java))
        }
    }

    private fun observeViewModel() {
        viewModel.state.observe(this) { state ->
            updateTimerDisplay(state)
            updateBackground(state)
            updateButtons(state)
        }
    }

    private fun updateTimerDisplay(state: TimerState) {
        val totalSecs = state.remainingMillis / 1000L
        val hours = totalSecs / 3600
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
    }

    private fun updateBackground(state: TimerState) {
        val colorHex = state.activePhase?.colorHex ?: "#2E7D32"
        val bgColor = Color.parseColor(colorHex)

        binding.rootLayout.setBackgroundColor(bgColor)

        val textColor = if (isColorDark(bgColor)) Color.WHITE else Color.parseColor("#212121")
        binding.tvTimer.setTextColor(textColor)
        binding.tvPhaseLabel.setTextColor(textColor)
        binding.progressArc.setIndicatorColor(lightenColor(bgColor, 0.4f))

        if (state.isFlashing) startFlashAnimation() else stopFlashAnimation()

        binding.tvPhaseLabel.text = when (state.phase) {
            TimerPhase.SETUP -> "Set your time"
            TimerPhase.RUNNING -> state.activePhase?.message ?: ""
            TimerPhase.PAUSED -> "Paused \u23F8"
            TimerPhase.FINISHED -> "Time's up! \u23F0"
        }
    }

    private fun updateButtons(state: TimerState) {
        binding.btnSettings.visibility = if (state.phase == TimerPhase.SETUP) View.VISIBLE else View.GONE

        when (state.phase) {
            TimerPhase.SETUP -> {
                binding.setupPanel.visibility = View.VISIBLE
                binding.btnStart.text = "Start"
                binding.btnStart.visibility = View.VISIBLE
                binding.btnPause.visibility = View.GONE
                binding.btnReset.visibility = View.GONE
            }
            TimerPhase.RUNNING -> {
                binding.setupPanel.visibility = View.GONE
                binding.btnStart.visibility = View.GONE
                binding.btnPause.visibility = View.VISIBLE
                binding.btnReset.visibility = View.VISIBLE
            }
            TimerPhase.PAUSED -> {
                binding.setupPanel.visibility = View.GONE
                binding.btnStart.text = "Resume"
                binding.btnStart.visibility = View.VISIBLE
                binding.btnPause.visibility = View.GONE
                binding.btnReset.visibility = View.VISIBLE
            }
            TimerPhase.FINISHED -> {
                binding.setupPanel.visibility = View.GONE
                binding.btnStart.visibility = View.GONE
                binding.btnPause.visibility = View.GONE
                binding.btnReset.visibility = View.VISIBLE
            }
        }
    }

    private fun isColorDark(color: Int): Boolean {
        val luminance = (0.299 * Color.red(color) +
                0.587 * Color.green(color) +
                0.114 * Color.blue(color)) / 255.0
        return luminance < 0.5
    }

    private fun lightenColor(color: Int, factor: Float): Int {
        val r = (Color.red(color) + (255 - Color.red(color)) * factor).toInt().coerceIn(0, 255)
        val g = (Color.green(color) + (255 - Color.green(color)) * factor).toInt().coerceIn(0, 255)
        val b = (Color.blue(color) + (255 - Color.blue(color)) * factor).toInt().coerceIn(0, 255)
        return Color.rgb(r, g, b)
    }

    private fun startFlashAnimation() {
        if (flashAnimation != null) return
        flashAnimation = AlphaAnimation(1f, 0.2f).apply {
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
    }
}
