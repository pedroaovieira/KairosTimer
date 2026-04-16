package com.presentationapp

import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import com.presentationapp.databinding.ActivitySettingsBinding

class SettingsActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySettingsBinding
    private lateinit var repository: PhasesRepository
    private lateinit var adapter: PhaseAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySettingsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = "Timer Phases"

        repository = PhasesRepository(this)
        adapter = PhaseAdapter(repository.loadPhases().toMutableList())

        binding.recyclerPhases.layoutManager = LinearLayoutManager(this)
        binding.recyclerPhases.adapter = adapter

        binding.fabAddPhase.setOnClickListener {
            adapter.addPhase(
                PhaseConfig(
                    name = "New phase",
                    thresholdPercent = 10,
                    colorHex = "#1565C0",
                    message = "New phase"
                )
            )
            binding.recyclerPhases.smoothScrollToPosition(adapter.itemCount - 1)
        }
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.menu_settings, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.action_save -> { save(); true }
            android.R.id.home -> { save(); finish(); true }
            else -> super.onOptionsItemSelected(item)
        }
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        save()
        @Suppress("DEPRECATION")
        super.onBackPressed()
    }

    private fun save() {
        val phases = adapter.getPhases()
        if (phases.isEmpty()) {
            Toast.makeText(this, "At least one phase is required", Toast.LENGTH_SHORT).show()
            return
        }
        repository.savePhases(phases)
        Toast.makeText(this, "Phases saved", Toast.LENGTH_SHORT).show()
    }
}
