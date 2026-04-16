package org.pedrov.presentationtimer

import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.text.Editable
import android.text.TextWatcher
import android.view.LayoutInflater
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.LinearLayout
import androidx.recyclerview.widget.RecyclerView
import org.pedrov.presentationtimer.databinding.ItemPhaseBinding

val PRESET_COLORS = listOf(
    "#1B5E20", "#2E7D32", "#66BB6A",
    "#F9A825", "#E65100", "#FF6D00",
    "#B71C1C", "#C62828", "#EF5350",
    "#1565C0", "#0D47A1", "#6A1B9A",
    "#37474F", "#00695C", "#4E342E"
)

class PhaseAdapter(private val phases: MutableList<PhaseConfig>) :
    RecyclerView.Adapter<PhaseAdapter.PhaseViewHolder>() {

    inner class PhaseViewHolder(val binding: ItemPhaseBinding) :
        RecyclerView.ViewHolder(binding.root) {
        var nameWatcher: TextWatcher? = null
        var thresholdWatcher: TextWatcher? = null
        var messageWatcher: TextWatcher? = null

        fun clearWatchers() {
            nameWatcher?.let { binding.etName.removeTextChangedListener(it) }
            thresholdWatcher?.let { binding.etThreshold.removeTextChangedListener(it) }
            messageWatcher?.let { binding.etMessage.removeTextChangedListener(it) }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): PhaseViewHolder {
        val binding = ItemPhaseBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return PhaseViewHolder(binding)
    }

    override fun onBindViewHolder(holder: PhaseViewHolder, position: Int) {
        holder.clearWatchers()

        val phase = phases[position]
        val b = holder.binding

        b.etName.setText(phase.name)
        b.etThreshold.setText(phase.thresholdPercent.toString())
        b.etMessage.setText(phase.message)

        setupColorSwatches(holder, phase)

        val canDelete = phases.size > 1
        b.btnDelete.isEnabled = canDelete
        b.btnDelete.alpha = if (canDelete) 1f else 0.3f
        b.btnDelete.setOnClickListener {
            val pos = holder.bindingAdapterPosition
            if (pos != RecyclerView.NO_ID.toInt() && phases.size > 1) {
                phases.removeAt(pos)
                notifyItemRemoved(pos)
                notifyItemRangeChanged(pos, phases.size)
            }
        }

        holder.nameWatcher = simpleWatcher { s ->
            val pos = holder.bindingAdapterPosition
            if (pos != RecyclerView.NO_ID.toInt()) phases[pos] = phases[pos].copy(name = s)
        }
        b.etName.addTextChangedListener(holder.nameWatcher)

        holder.thresholdWatcher = simpleWatcher { s ->
            val pos = holder.bindingAdapterPosition
            if (pos != RecyclerView.NO_ID.toInt()) {
                val v = s.toIntOrNull()?.coerceIn(0, 100) ?: 0
                phases[pos] = phases[pos].copy(thresholdPercent = v)
            }
        }
        b.etThreshold.addTextChangedListener(holder.thresholdWatcher)

        holder.messageWatcher = simpleWatcher { s ->
            val pos = holder.bindingAdapterPosition
            if (pos != RecyclerView.NO_ID.toInt()) phases[pos] = phases[pos].copy(message = s)
        }
        b.etMessage.addTextChangedListener(holder.messageWatcher)
    }

    private fun setupColorSwatches(holder: PhaseViewHolder, phase: PhaseConfig) {
        val ctx = holder.itemView.context
        val dp = ctx.resources.displayMetrics.density
        val size = (36 * dp).toInt()
        val margin = (8 * dp).toInt()
        val strokeWidth = (3 * dp).toInt()

        val container = holder.binding.colorSwatches
        container.removeAllViews()

        PRESET_COLORS.forEach { hex ->
            val circle = ImageView(ctx).apply {
                layoutParams = LinearLayout.LayoutParams(size, size).also { it.marginEnd = margin }
                val drawable = GradientDrawable().apply {
                    shape = GradientDrawable.OVAL
                    setColor(Color.parseColor(hex))
                    if (hex.equals(phase.colorHex, ignoreCase = true)) {
                        setStroke(strokeWidth, Color.WHITE)
                    }
                }
                setImageDrawable(drawable)
                setOnClickListener {
                    val pos = holder.bindingAdapterPosition
                    if (pos != RecyclerView.NO_ID.toInt()) {
                        phases[pos] = phases[pos].copy(colorHex = hex)
                        setupColorSwatches(holder, phases[pos])
                    }
                }
            }
            container.addView(circle)
        }
    }

    private fun simpleWatcher(onChanged: (String) -> Unit) = object : TextWatcher {
        override fun afterTextChanged(s: Editable?) { onChanged(s?.toString() ?: "") }
        override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
        override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
    }

    override fun getItemCount() = phases.size

    fun addPhase(phase: PhaseConfig) {
        phases.add(phase)
        notifyItemInserted(phases.size - 1)
    }

    fun getPhases(): List<PhaseConfig> = phases.toList()
}
