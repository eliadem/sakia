from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import QEvent, QLocale, pyqtSignal
from .informations_uic import Ui_InformationsWidget
from enum import Enum
from sakia.helpers import timestamp_to_dhms
from sakia.constants import ROOT_SERVERS
from sakia.gui.widgets.dialogs import dialog_async_exec


class InformationsView(QWidget, Ui_InformationsWidget):
    """
    The view of navigation panel
    """
    retranslate_required = pyqtSignal()

    class CommunityState(Enum):
        NOT_INIT = 0
        OFFLINE = 1
        READY = 2

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.scrollarea.hide()
        self.button_details.clicked.connect(self.handle_details_click)

    def handle_details_click(self):
        if self.button_details.isChecked():
            self.scrollarea.show()
        else:
            self.scrollarea.hide()

    def set_simple_informations(self, data, state):
        if state in (InformationsView.CommunityState.NOT_INIT, InformationsView.CommunityState.OFFLINE):
            self.label_currency.setText("""<html>
                <body>
                <p>
                <span style=" font-size:16pt; font-weight:600;">{currency}</span>
                </p>
                <p>{message}</p>
                </body>
                </html>""".format(currency=data['currency'],
                                  message=InformationsView.simple_message[state]))
            self.button_membership.hide()
        else:
            status_value = self.tr("Member") if data['membership_state'] else self.tr("Non-Member")
            if data['mstime'] > 0:
                membership_action_value = self.tr("Renew membership")
                status_info = ""
                membership_action_enabled = True
            elif data['membership_state']:
                membership_action_value = self.tr("Renew membership")
                status_info = "Your membership expired"
                membership_action_enabled = True
            else:
                membership_action_value = self.tr("Request membership")
                if data['nb_certs'] > data['nb_certs_required']:
                    status_info = self.tr("Registration ready")
                    membership_action_enabled = True
                else:
                    status_info = self.tr("{0} more certifications required")\
                        .format(data['nb_certs_required'] - data['nb_certs'])
                    membership_action_enabled = True

            if data['mstime'] > 0:
                days, hours, minutes, seconds = timestamp_to_dhms(data['mstime'])
                mstime_remaining_text = self.tr("Expires in ")
                if days > 0:
                    mstime_remaining_text += "{days} days".format(days=days)
                else:
                    mstime_remaining_text += "{hours} hours and {min} min.".format(hours=hours,
                                                                                   min=minutes)
            else:
                mstime_remaining_text = self.tr("Expired or never published")

            status_color = '#00AA00' if data['membership_state'] else self.tr('#FF0000')
            description_currency = """<html>
<body>
    <p>
        <span style=" font-size:16pt; font-weight:600;">{currency}</span>
    </p>
    <p>{nb_members} {members_label}</p>
    <p><span style="font-weight:600;">{monetary_mass_label}</span> : {monetary_mass}</p>
    <p><span style="font-weight:600;">{balance_label}</span> : {balance}</p>
</body>
</html>""".format(currency=data['currency'],
                  nb_members=data['members_count'],
                  members_label=self.tr("members"),
                  monetary_mass_label=self.tr("Monetary mass"),
                  monetary_mass=data['mass'],
                  balance_label=self.tr("Balance"),
                  balance=data['amount'])

            description_membership = """<html>
<body>
    <p><span style="font-weight:600;">{status_label}</span>
     : <span style="color:{status_color};">{status}</span>
     - <span>{status_info}</span></p>
</body>
</html>""".format(status_color=status_color,
                  status_label=self.tr("Status"),
                  status=status_value,
                  status_info=status_info)
            description_identity = """<html>
<body>
    <p><span style="font-weight:600;">{nb_certs_label}</span> : {nb_certs} ({outdistanced_text})</p>
    <p><span style="font-weight:600;">{mstime_remaining_label}</span> : {mstime_remaining}</p>
</body>
</html>""".format(nb_certs_label=self.tr("Certs. received"),
                  nb_certs=data['nb_certs'],
                  outdistanced_text=data['outdistanced'],
                  mstime_remaining_label=self.tr("Membership"),
                  mstime_remaining=mstime_remaining_text)

            self.label_currency.setText(description_currency)

            if data['is_identity']:
                self.label_membership.setText(description_membership)
                self.label_identity.setText(description_identity)
                self.button_membership.setText(membership_action_value)
                self.button_membership.setEnabled(membership_action_enabled)
            else:
                self.label_membership.hide()
                self.label_identity.hide()
                self.button_membership.hide()

    def set_general_text_no_dividend(self):
        """
        Set the general text when there is no dividend
        """
        self.label_general.setText(self.tr('No Universal Dividend created yet.'))

    def set_general_text(self, localized_data):
        """
        Fill the general text with given informations
        :return:
        """
        # set infos in label
        self.label_general.setText(
            self.tr("""
            <table cellpadding="5">
            <tr><td align="right"><b>{:}</b></div></td><td>{:} {:}</td></tr>
            <tr><td align="right"><b>{:}</b></td><td>{:} {:}</td></tr>
            <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
            <tr><td align="right"><b>{:}</b></td><td>{:} {:}</td></tr>
            <tr><td align="right"><b>{:2.2%} / {:} days</b></td><td>{:}</td></tr>
            <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
            <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
            <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
            <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
            </table>
            """).format(
                localized_data.get('ud', '####'),
                self.tr('Universal Dividend UD(t) in'),
                localized_data['diff_units'],
                localized_data.get('mass_minus_1', "###"),
                self.tr('Monetary Mass M(t-1) in'),
                localized_data['units'],
                localized_data.get('members_count', '####'),
                self.tr('Members N(t)'),
                localized_data.get('mass_minus_1_per_member', '####'),
                self.tr('Monetary Mass per member M(t-1)/N(t) in'),
                localized_data['diff_units'],
                localized_data.get('actual_growth', 0),
                localized_data.get('days_per_dividend', '####'),
                self.tr('Actual growth c = UD(t)/[M(t-1)/N(t)]'),
                localized_data.get('ud_median_time_minus_1', '####'),
                self.tr('Penultimate UD date and time (t-1)'),
                localized_data.get('ud_median_time', '####'),
                self.tr('Last UD date and time (t)'),
                localized_data.get('next_ud_median_time', '####'),
                self.tr('Next UD date and time (t+1)'),
                localized_data.get('next_ud_reeaval', '####'),
                self.tr('Next UD reevaluation (t+1)')
            )
        )

    def set_rules_text_no_dividend(self):
        """
        Set text when no dividends was generated yet
        """
        self.label_rules.setText(self.tr('No Universal Dividend created yet.'))

    def set_rules_text(self, localized_data):
        """
        Set text in rules
        :param dict localized_data:
        :return:
        """
        # set infos in label
        self.label_rules.setText(
            self.tr("""
            <table cellpadding="5">
            <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
            <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
            <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
            </table>
            """).format(
                self.tr('{:2.0%} / {:} days').format(localized_data['growth'], localized_data['days_per_dividend']),
                self.tr('Fundamental growth (c) / Delta time (dt)'),
                self.tr('UDĞ(t) = UDĞ(t-1) + c²*M(t-1)/N(t-1)'),
                self.tr('Universal Dividend (formula)'),
                self.tr('{:} = {:} + {:2.0%}²* {:} / {:}').format(
                    localized_data.get('ud_plus_1', '####'),
                    localized_data.get('ud', '####'),
                    localized_data.get('growth', '####'),
                    localized_data.get('mass', '####'),
                    localized_data.get('members_count', '####')
                ),
                self.tr('Universal Dividend (computed)')
            )
        )

    def set_text_referentials(self, referentials):
        """
        Set text from referentials
        :param list referentials: list of referentials
        """
        # set infos in label
        ref_template = """
                <table cellpadding="5">
                <tr><th>{:}</th><td>{:}</td></tr>
                <tr><th>{:}</th><td>{:}</td></tr>
                <tr><th>{:}</th><td>{:}</td></tr>
                <tr><th>{:}</th><td>{:}</td></tr>
                </table>
                """
        templates = []
        for ref in referentials:
            # print(ref_class.__class__.__name__)
            # if ref_class.__class__.__name__ == 'RelativeToPast':
            #     continue
            templates.append(ref_template.format(self.tr('Name'), ref.translated_name(),
                                                 self.tr('Units'), ref.units,
                                                 self.tr('Formula'), ref.formula,
                                                 self.tr('Description'), ref.description
                                                 )
                             )

        self.label_referentials.setText('<hr>'.join(templates))

    def set_money_text(self, params, currency):
        """
        Set text from money parameters
        :param sakia.data.entities.BlockchainParameters params: Parameters of the currency
        :param str currency: The currency
        """

        dt_dhms = timestamp_to_dhms(params.dt)
        if dt_dhms[0] > 0:
            dt_as_str = self.tr("{:} day(s) {:} hour(s)").format(*dt_dhms)
        else:
            dt_as_str = self.tr("{:} hour(s)").format(dt_dhms[1])
        if dt_dhms[2] > 0 or dt_dhms[3] > 0:
            dt_dhms += ", {:} minute(s) and {:} second(s)".format(*dt_dhms[1:])
        dt_reeval_dhms = timestamp_to_dhms(params.dt_reeval)
        dt_reeval_as_str = self.tr("{:} day(s) {:} hour(s)").format(*dt_reeval_dhms)


        # set infos in label
        self.label_money.setText(
                self.tr("""
            <table cellpadding="5">
            <tr><td align="right"><b>{:2.0%} / {:} days</b></td><td>{:}</td></tr>
            <tr><td align="right"><b>{:}</b></td><td>{:} {:}</td></tr>
            <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
            <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
            <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
            <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
            <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
            <tr><td align="right"><b>{:2.0%}</b></td><td>{:}</td></tr>
            </table>
            """).format(
                        params.c,
                        QLocale().toString(params.dt / 86400, 'f', 2),
                        self.tr('Fundamental growth (c)'),
                        params.ud0,
                        self.tr('Initial Universal Dividend UD(0) in'),
                        currency,
                        dt_as_str,
                        self.tr('Time period between two UD'),
                        dt_reeval_as_str,
                        self.tr('Time period between two UD reevaluation'),
                        params.median_time_blocks,
                        self.tr('Number of blocks used for calculating median time'),
                        params.avg_gen_time,
                        self.tr('The average time in seconds for writing 1 block (wished time)'),
                        params.dt_diff_eval,
                        self.tr('The number of blocks required to evaluate again PoWMin value'),
                        params.percent_rot,
                        self.tr('The percent of previous issuers to reach for personalized difficulty')
                )
        )

    def set_wot_text(self, params):
        """
        Set wot text from currency parameters
        :param sakia.data.entities.BlockchainParameters params: Parameters of the currency
        :return:
        """

        # set infos in label
        self.label_wot.setText(
                self.tr("""
            <table cellpadding="5">
<tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
<tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
<tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
<tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
<tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
<tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
<tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
<tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
</table>
""").format(
            QLocale().toString(params.sig_period / 86400, 'f', 2),
            self.tr('Minimum delay between 2 certifications (in days)'),
            QLocale().toString(params.sig_validity / 86400, 'f', 2),
            self.tr('Maximum age of a valid signature (in days)'),
            params.sig_qty,
            self.tr('Minimum quantity of signatures to be part of the WoT'),
            params.sig_stock,
            self.tr('Maximum quantity of active certifications made by member.'),
            params.sig_window,
            self.tr('Maximum delay a certification can wait before being expired for non-writing.'),
            params.xpercent,
            self.tr('Minimum percent of sentries to reach to match the distance rule'),
            params.ms_validity / 86400,
            self.tr('Maximum age of a valid membership (in days)'),
            params.step_max,
            self.tr('Maximum distance between each WoT member and a newcomer'),
                )
        )

    async def licence_dialog(self, currency, params):
        dt_dhms = timestamp_to_dhms(params.dt)
        if dt_dhms[0] > 0:
            dt_as_str = self.tr("{:} day(s) {:} hour(s)").format(*dt_dhms)
        else:
            dt_as_str = self.tr("{:} hour(s)").format(dt_dhms[1])
        if dt_dhms[2] > 0 or dt_dhms[3] > 0:
            dt_dhms += ", {:} minute(s) and {:} second(s)".format(*dt_dhms[1:])
        dt_reeval_dhms = timestamp_to_dhms(params.dt_reeval)
        dt_reeval_as_str = self.tr("{:} day(s) {:} hour(s)").format(*dt_reeval_dhms)

        message_box = QMessageBox(self)

        message_box.setText("Do you recognize the terms of the following licence :")
        message_box.setInformativeText("""
{:} is being produced by a Universal Dividend (UD) for any human member, which is :<br/>
<br/>
<table cellpadding="5">
 <tr><td align="right"><b>{:2.0%} / {:} days</b></td><td>{:}</td></tr>
 <tr><td align="right"><b>{:}</b></td><td>{:} {:}</td></tr>
 <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
 <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
</table>
<br/>
<br/>

The parameters of the Web of Trust of {:} are :<br/>
<table cellpadding="5">
 <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
 <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
 <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
 <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
 <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
 <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
 <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
 <tr><td align="right"><b>{:}</b></td><td>{:}</td></tr>
</table>
<br/>
<br/>

<b>By asking to join as member, you recognize that this is your unique account,
and that you will only certify persons that you know well enough.</b>
 """.format(
            ROOT_SERVERS[currency]["display"],
            params.c,
            QLocale().toString(params.dt / 86400, 'f', 2),
            self.tr('Fundamental growth (c)'),
            params.ud0,
            self.tr('Initial Universal Dividend UD(0) in'),
            ROOT_SERVERS[currency]["display"],
            dt_as_str,
            self.tr('Time period between two UD'),
            dt_reeval_as_str,
            self.tr('Time period between two UD reevaluation'),
            ROOT_SERVERS[currency]["display"],
            QLocale().toString(params.sig_period / 86400, 'f', 2),
            self.tr('Minimum delay between 2 certifications (in days)'),
            QLocale().toString(params.sig_validity / 86400, 'f', 2),
            self.tr('Maximum age of a valid signature (in days)'),
            params.sig_qty,
            self.tr('Minimum quantity of signatures to be part of the WoT'),
            params.sig_stock,
            self.tr('Maximum quantity of active certifications made by member.'),
            params.sig_window,
            self.tr('Maximum delay a certification can wait before being expired for non-writing.'),
            params.xpercent,
            self.tr('Minimum percent of sentries to reach to match the distance rule'),
            params.ms_validity / 86400,
            self.tr('Maximum age of a valid membership (in days)'),
            params.step_max,
            self.tr('Maximum distance between each WoT member and a newcomer'),
        )
    )
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No )
        message_box.setDefaultButton(QMessageBox.No)
        return await dialog_async_exec(message_box)

    def changeEvent(self, event):
        """
        Intercepte LanguageChange event to translate UI
        :param QEvent QEvent: Event
        :return:
        """
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi(self)
        return super().changeEvent(event)
