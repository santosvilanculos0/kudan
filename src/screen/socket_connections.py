from datetime import datetime
from logging import WARNING

from more_itertools import unique
from psutil import Process, _common, net_connections
from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QHideEvent, QShowEvent, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from env import logger


class SocketConnections(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.logger = logger()

        q_v_box_layout = QVBoxLayout(self)
        q_v_box_layout.setContentsMargins(0, 0, 0, 0)
        q_v_box_layout.setSpacing(0)

        # h = QWidget()
        # h.setFixedHeight(44)
        # h.setStyleSheet(
        #     "QWidget{border-bottom:1px solid #e0e0e0;background-color:#fff}"
        # )
        # q_v_box_layout.addWidget(h)

        self.q_table_widget = QTableWidget()
        # self.q_table_widget.setStyleSheet("QTableWidget{border:0}")
        self.q_table_widget.setColumnCount(9)
        self.q_table_widget.setHorizontalHeaderLabels(
            [
                "pid",
                "name",
                "fd",
                "family",
                "type",
                "laddr",
                "raddr",
                "status",
                "create_time",
            ]
        )
        self.q_table_widget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.q_table_widget.verticalHeader().setHidden(True)
        self.q_table_widget.setAutoScroll(True)
        self.q_table_widget.setVerticalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel
        )
        self.q_table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.q_table_widget.setAlternatingRowColors(True)
        self.q_table_widget.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.q_table_widget.setContextMenuPolicy(
            Qt.ContextMenuPolicy.ActionsContextMenu
        )
        self.q_table_widget.addAction("Kill process", self.process_kill)

        for index, sconn in enumerate(net_connections()):
            self.q_table_widget_insert_row(index, sconn)

        self.q_table_widget.setSortingEnabled(True)
        self.q_table_widget.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        q_v_box_layout.addWidget(self.q_table_widget)

        self.q_timer = QTimer(self)
        self.q_timer.setInterval(1_000)
        self.q_timer.timeout.connect(self.q_timer_timeout)

    def q_table_widget_insert_row(self, row: int, sconn: _common.sconn) -> None:
        self.q_table_widget.setSortingEnabled(False)
        self.q_table_widget.insertRow(row)
        self.q_table_widget.setRowHeight(row, 36)

        column = 0
        pid = QTableWidgetItem(str(sconn.pid))
        pid.setData(Qt.ItemDataRole.UserRole, sconn.pid)
        self.q_table_widget.setItem(row, column, pid)

        column = 1
        name = QTableWidgetItem()
        try:
            process = Process(sconn.pid)
            name.setText(process.name())
        except Exception as exception:
            pass
        self.q_table_widget.setItem(row, column, name)

        column = 2
        fd = QTableWidgetItem(str(sconn.fd))
        self.q_table_widget.setItem(row, column, fd)

        column = 3
        family = QTableWidgetItem(str(sconn.family.name))
        self.q_table_widget.setItem(row, column, family)

        column = 4
        type = QTableWidgetItem(str(sconn.type.name))
        self.q_table_widget.setItem(row, column, type)

        column = 5
        q_url = QUrl()
        if isinstance(sconn.laddr, _common.addr):
            q_url.setHost(sconn.laddr.ip)
            q_url.setPort(sconn.laddr.port)
        laddr = QTableWidgetItem(
            str(q_url.url(QUrl.ComponentFormattingOption.EncodeUnicode))
        )
        self.q_table_widget.setItem(row, column, laddr)

        column = 6
        q_url.clear()
        if isinstance(sconn.raddr, _common.addr):
            q_url.setHost(sconn.raddr.ip)
            q_url.setPort(sconn.raddr.port)
        raddr = QTableWidgetItem(
            q_url.url(QUrl.ComponentFormattingOption.EncodeUnicode)
        )
        self.q_table_widget.setItem(row, column, raddr)

        column = 7
        status = QTableWidgetItem(str(sconn.status))
        self.q_table_widget.setItem(row, column, status)

        column = 8
        create_time = QTableWidgetItem()
        try:
            process = Process(sconn.pid)
            create_time.setText(
                datetime.fromtimestamp(process.create_time()).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )
        except Exception as exception:
            pass
        self.q_table_widget.setItem(row, column, create_time)

        self.q_table_widget.setSortingEnabled(True)

    def q_timer_timeout(self) -> None:
        sconn_list = net_connections()
        sconn_unique_pid_list = list(unique(sconn.pid for sconn in sconn_list))

        index = 0
        while index < self.q_table_widget.rowCount():
            pid = int(self.q_table_widget.item(index, 0).text())
            if sconn_unique_pid_list.count(pid) == 0:
                self.q_table_widget.removeRow(index)
            else:
                sconn_unique_pid_list.remove(pid)
            index += 1

        sconn_list = list(
            filter(lambda sconn: sconn_unique_pid_list.count(sconn.pid) > 0, sconn_list)
        )

        for index, sconn in enumerate(sconn_list, self.q_table_widget.rowCount()):
            self.q_table_widget_insert_row(index, sconn)

    def showEvent(self, event: QShowEvent) -> None:
        self.q_timer.start()
        return super().showEvent(event)

    def hideEvent(self, event: QHideEvent) -> None:
        self.q_timer.stop()
        return super().hideEvent(event)

    def process_kill(self) -> None:
        q_table_widget_selected_items = self.q_table_widget.selectedItems()
        if len(q_table_widget_selected_items) > 0:
            row_list = list(
                unique(
                    self.q_table_widget.row(x)
                    for x in self.q_table_widget.selectedItems()
                )
            )
            for row in row_list:
                pid = int(self.q_table_widget.item(row, 0).text())
                try:
                    process = Process(pid)
                    process.kill()
                except Exception as exception:
                    self.logger.log(WARNING, f"Unable to kill process (pid={pid})")