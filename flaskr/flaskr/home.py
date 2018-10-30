# -*- coding: utf-8 -*-
# author: zyk

from flask import Flask
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('home', __name__, url_prefix='/home')


@bp.route("/")
def main():
    return render_template("self/index.html")