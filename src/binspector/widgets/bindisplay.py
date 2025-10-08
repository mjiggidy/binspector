from PySide6 import QtWidgets
import avbutils
from .. import views

class LBBinDisplayItemTypesView(views.LBAbstractEnumFlagsView):
	"""Flags for setting Bin Item Display filter"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		
		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().setSpacing(0)
		self.layout().setContentsMargins(3,0,3,0)

		grp_clips = QtWidgets.QGroupBox(title="Clip Types")

		grp_clips.setLayout(QtWidgets.QVBoxLayout())
		grp_clips.layout().setSpacing(0)
		grp_clips.layout().setContentsMargins(3,0,3,0)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.MASTER_CLIP]
		chk.setText("Master Clips")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.LINKED_MASTER_CLIP]
		chk.setText("Linked Master Clips")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.SUBCLIP]
		chk.setText("Subclips")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.SEQUENCE]
		chk.setText("Sequences")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.SOURCE]
		chk.setText("Sources")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.EFFECT]
		chk.setText("Effects")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.MOTION_EFFECT]
		chk.setText("Motion Effects")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.PRECOMP_RENDERED_EFFECT]
		chk.setText("Precompute Clips - Rendered Effects")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.PRECOMP_TITLE_MATTEKEY]
		chk.setText("Precompute Clips - Titles and Matte Keys")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.GROUP]
		chk.setText("Groups")
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.STEREOSCOPIC_CLIP]
		chk.setText("Stereoscopic Clips")
		grp_clips.layout().addWidget(chk)

		self.layout().addWidget(grp_clips)

		grp_origins = QtWidgets.QGroupBox(title="Clip Origins")
		grp_origins.setLayout(QtWidgets.QVBoxLayout())
		grp_origins.layout().setSpacing(0)
		grp_origins.layout().setContentsMargins(3,0,3,0)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.USER_CLIP]
		chk.setText("Show clips created by user")
		grp_origins.layout().addWidget(chk)
		
		chk = self._option_mappings[avbutils.BinDisplayItemTypes.REFERENCE_CLIP]
		chk.setText("Show reference clips")
		grp_origins.layout().addWidget(chk)
		

		self.layout().addWidget(grp_origins)

		self.layout().addStretch()